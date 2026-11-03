"""Import one saved public teaching evaluation into Langfuse. No LLM calls."""
import argparse
import hashlib
from getpass import getpass
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
import uuid

ROOT = Path(__file__).resolve().parent
SCORE_NAMES = {"evidence": "依据一致性", "coverage": "回答完整性"}
TRACE_NAME = "learning-saved-evaluation-import"


def build_payload(report_path=None, case_path=None):
    if report_path is None:
        files = list((ROOT.parent / "deepeval" / "results").glob("dimensions-*.json"))
        if not files:
            raise ValueError("尚无双指标报告，请先完成第13节")
        report_path = max(files, key=lambda p: p.stat().st_mtime)
    report_path = Path(report_path)
    case_path = Path(case_path) if case_path else ROOT.parent / "promptfoo" / "judge-cases.json"
    source = report_path.read_bytes()
    report = json.loads(source)
    if report.get("case_file_sha256") != hashlib.sha256(case_path.read_bytes()).hexdigest():
        raise ValueError("样例版本与报告不一致，停止导入")
    case = next(case for case in json.loads(case_path.read_text(encoding="utf-8")) if case["description"] == "j05")
    rows = [row for row in report["rows"] if row["id"] == "j05"]
    if len(rows) != 2 or {row["metric"] for row in rows} != set(SCORE_NAMES):
        raise ValueError("j05需要两个不同维度的完整结果")
    scores = []
    for row in rows:
        if row.get("status") != "graded" or type(row.get("score")) not in (int, float) or row["score"] not in (0, 1):
            raise ValueError("报告含执行错误或无效判分，不冒充有效0分")
        if type(row.get("pass")) is not bool or row["pass"] != bool(row["score"]):
            raise ValueError("报告的分数与通过状态不一致")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError("报告缺少判分理由")
        scores.append({"key": row["metric"], "name": SCORE_NAMES[row["metric"]], "value": float(row["score"]), "reason": row["reason"]})
    return {
        "record_type": "import_of_saved_synthetic_evaluation",
        "source_file": report_path.name,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "case_id": "j05",
        "question": case["vars"]["question"],
        "reference_documents": case["vars"]["context_text"],
        "candidate_answer": json.loads(case["vars"]["candidate"])["answer"],
        "original_judge_model": report.get("judge_model"),
        "original_requests_attempted": report.get("requests_attempted"),
        "scores": scores,
        "new_model_calls": 0,
        "timing_scope": "Import operations only; original judge latency is not reconstructed",
    }


def emit_trace(client, payload):
    """Record actual import work; do not invent a historical generation span."""
    with client.start_as_current_observation(
        name=TRACE_NAME, as_type="span",
        input={"question": payload["question"]},
        metadata={"recordtype": payload["record_type"], "sourcefile": payload["source_file"],
                  "sourcehash": payload["source_sha256"], "timingscope": payload["timing_scope"]},
    ) as root:
        with client.start_as_current_observation(name="prepare-case-display", as_type="span") as preparation:
            display = {key: payload[key] for key in ("question", "reference_documents", "candidate_answer")}
            preparation.update(output=display)
        with client.start_as_current_observation(name="attach-existing-scores", as_type="span") as scoring:
            for score in payload["scores"]:
                client.create_score(
                    name=score["name"], value=score["value"], data_type="NUMERIC",
                    trace_id=root.trace_id, comment=score["reason"],
                    metadata={"source": "saved DeepEval GEval result", "sourcefile": payload["source_file"]},
                )
            scoring.update(output={"attached_score_names": [score["name"] for score in payload["scores"]], "new_model_calls": 0})
        root.update(output={"answer": payload["candidate_answer"], "saved_scores": {score["name"]: score["value"] for score in payload["scores"]}})
        return root.trace_id


def credentials():
    public = os.environ.get("LANGFUSE_PUBLIC_KEY", "").strip()
    secret = os.environ.get("LANGFUSE_SECRET_KEY", "").strip()
    base = os.environ.get("LANGFUSE_BASE_URL", "").strip().rstrip("/")
    if (not public or not secret or not base) and sys.stdin.isatty():
        print("只在当前服务器终端输入，密钥不会显示或写入文件。")
        if not base:
            base = input("Langfuse区域根地址，US项目直接回车：https://us.cloud.langfuse.com ：").strip() or "https://us.cloud.langfuse.com"
            base = base.rstrip("/")
        if not public:
            public = getpass("输入项目Public Key后回车：").strip()
        if not secret:
            secret = getpass("输入项目Secret Key后回车：").strip()
    if not public or not secret or not base:
        raise ValueError("请在当前终端设置LANGFUSE_PUBLIC_KEY、LANGFUSE_SECRET_KEY、LANGFUSE_BASE_URL")
    if not public.startswith("pk-lf-") or not secret.startswith("sk-lf-"):
        raise ValueError("需要Langfuse项目密钥对，不能使用DeepSeek密钥")
    parts = urlsplit(base)
    allowed = {"cloud.langfuse.com", "us.cloud.langfuse.com", "jp.cloud.langfuse.com", "hipaa.cloud.langfuse.com"}
    if parts.scheme != "https" or parts.netloc not in allowed or parts.path or parts.query or parts.fragment:
        raise ValueError("本节只连接官方Langfuse Cloud区域根地址，请核对BASE_URL")
    return public, secret, base


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--payload-json", action="store_true")
    mode.add_argument("--send", action="store_true")
    args = parser.parse_args()
    try:
        payload = build_payload()
    except (ValueError, KeyError, StopIteration) as error:
        parser.exit(1, f"无法准备导入材料：{error}\n")
    if args.payload_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if not args.send:
        print("来源：", payload["source_file"])
        print("问题：", payload["question"])
        print("资料：", payload["reference_documents"])
        print("待评答案：", payload["candidate_answer"])
        for score in payload["scores"]:
            print(score["name"], "=", score["value"], "；已有裁判理由：", score["reason"])
        print("准备创建的记录树：导入已有评测 → 整理展示材料 / 附加已有分数。")
        print("仅预览，没有上传，没有新模型调用；--send才连接Langfuse Cloud。")
        return
    try:
        public, secret, base = credentials()
    except ValueError as error:
        parser.exit(1, str(error) + "\n")
    from langfuse import Langfuse
    client = Langfuse(public_key=public, secret_key=secret, base_url=base, timeout=10)
    try:
        if not client.auth_check():
            parser.exit(1, "鉴权未通过，请核对项目密钥与区域地址。\n")
        trace_id = emit_trace(client, payload)
        client.flush()
        url = client.get_trace_url(trace_id=trace_id)
        receipt = {"status": "submission_attempted_not_ui_verified", "trace_id": trace_id, "url": url,
                   "source_sha256": payload["source_sha256"], "new_model_calls": 0}
        directory = ROOT / "results"
        directory.mkdir(exist_ok=True)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        (directory / f"submission-{run_id}.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("已发起发送并刷新队列；需在网页看到记录和两个分数后确认接入成功。")
        print("Trace ID：", trace_id)
        if url:
            print("查看链接：", url)
        print("本轮没有调用DeepSeek；页面耗时只代表导入过程，不是此前模型耗时。")
    finally:
        client.shutdown()


if __name__ == "__main__":
    main()
