"""Render only synthetic evaluation artifacts. No network/model requests."""
import html
import json
import sys
from pathlib import Path

source, md_out, html_out = map(Path, sys.argv[1:4])
report = json.loads(source.read_text(encoding="utf-8"))
rows = report["results"]
lines = ["# Agent Desk 首轮真实后端评测", "", "日期：2026-11-05。AI协助准备并执行；学习者人工复核待完成。", "", "8个任务，9次真实DeepSeek生成，0次模型裁判。规则初筛7/8通过，1个失败，接口错误0。", "", "对象：本地含未提交改动的Agent Desk源码后端。不是GitHub旧版，不是已安装Electron包的界面测试。使用独立数据库、虚构资料与本机网关；生成配置覆盖为512输出token、关闭thinking、temperature=0。", "", "## 一眼看结果", "", "| 任务 | 要测什么 | 规则初筛 |", "|---|---|---|"]
for row in rows:
    lines.append(f'| {row["id"]} | {row["name"]} | {"通过" if row.get("rule_pass") else "未通过"} |')
lines += ["", "## 失败原因：ad02", "", "已建知识文档写着“灯塔项目使用 pnpm 安装依赖”，但问“第三方包该用哪个工具装”时未召回。模型实际请求只有发布代号记忆，没有安装工具资料，因此未回答pnpm。回答又把手工记忆ID写成了不存在的知识库引用。", "", "这是检索遗漏和引用编造两个问题。不是仅凭答案不好猜测：原始JSON中有实际参考资料、模型收到的messages及失败检查。引用检查后来离线补充，未再请求模型；记录在offline_regrade字段。", "", "## 每题证据"]
for row in rows:
    lines += ["", f'### {row["id"]} {row["name"]}', "", "问题：" + row["question"], "", "实际召回资料键：" + ", ".join(row["source_keys"]), "", "回答：", "", row.get("answer", "未生成"), "", "失败检查："]
    bad = [c["name"] for c in row["checks"] if not c["pass"]]
    lines += ["- " + name for name in bad] if bad else ["无；规则初筛通过，语义质量仍待人工复核。"]
    lines += ["", "人工标准：" + row["human_criterion"]]
lines += ["", "## 如何复现与解释", "", "见[运行说明](../evals/agentdesk/README.md)和[第16节](../docs/learning/016-agentdesk-project-evaluation.md)。", "", "代码规则验证指定事实、检索命中、引用ID、项目和会话隔离等，并非通用语义裁判。拒答正则可能漏判，引用存在不代表语义蕴含，AI生成的题目也需要人工复核。8题是开发集，不是独立基准。", "", "单题elapsed_ms是应用任务耗时，多轮题包含两次生成，不是单次模型延迟；usage只记录最终一轮，不能拿来计算全批次总token或费用。源码记录Git提交和5个关键文件哈希；未提交的其他源码未归档，不能只用GitHub提交完全重现。", "", "本轮尚未上传Langfuse，也不会自动出现在原promptfoo网页。后续先固定数据集并改进检索，再将真实应用轨迹和评分接到平台。", ""]
md_out.parent.mkdir(parents=True, exist_ok=True)
md_out.write_text("\n".join(lines), encoding="utf-8")
e = html.escape
cards = []
for row in rows:
    bad = [c["name"] for c in row["checks"] if not c["pass"]]
    requests = json.dumps(row.get("requests", []), ensure_ascii=False, indent=2)
    refs = json.dumps(row["reference_documents"], ensure_ascii=False, indent=2)
    cards.append(f'''<article><h2>{e(row['id'])} · {e(row['name'])} <b class="{'ok' if row['rule_pass'] else 'bad'}">{'规则通过' if row['rule_pass'] else '发现问题'}</b></h2>
<h3>用户问什么</h3><p>{e(row['question'])}</p><h3>应用回答什么</h3><blockquote>{e(row.get('answer','未生成'))}</blockquote>
<h3>失败检查</h3><p>{e('；'.join(bad) if bad else '没有失败项；这不代替人工语义复核。')}</p>
<details><summary>展开：应用实际检索到什么资料</summary><pre>{e(refs)}</pre></details>
<details><summary>展开：模型实际收到的完整消息（只有虚构实验数据）</summary><pre>{e(requests)}</pre></details>
<p class="muted">人工复核标准：{e(row['human_criterion'])}</p></article>''')
html_out.parent.mkdir(parents=True, exist_ok=True)
html_out.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agent Desk 第一轮项目评测</title><style>body{font:17px/1.75 system-ui,sans-serif;max-width:1050px;margin:auto;padding:35px;color:#1b293a;background:#f5f7fa}header,article{background:white;border:1px solid #dce1e8;border-radius:14px;padding:24px;margin:20px 0}h1{font-size:30px}h2{font-size:21px}h3{font-size:17px;margin-bottom:6px}.ok{color:#097248}.bad{color:#b32925}b{font-size:15px}blockquote{margin:0;padding:16px;background:#f2f6fa;white-space:pre-wrap;overflow-wrap:anywhere}pre{font:14px/1.6 monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:16px}summary{cursor:pointer;padding:8px 0}.muted{color:#657185;font-size:14px}</style><header><h1>Agent Desk · 首轮真实项目评测</h1><p>2026-11-05 · 本地源码后端 · DeepSeek生成 · 独立虚构实验数据</p><p><strong>8个任务 / 9次生成请求 / 规则初筛7项通过 / 1项失败 / 0次AI裁判</strong></p><p>重点看ad02：资料说“使用pnpm安装依赖”，用户换成问“第三方包”，检索没找到它，回答还编造了知识库引用。展开该题，查看模型实际收到的消息。</p><p>本轮使用代码检查事实、引用ID和隔离条件；人工语义复核待完成。不是综合正确率，不含桌面UI、文件任务执行，不是模拟答案。生成上限512 token、thinking关闭、temperature=0；没有自动上传Langfuse或promptfoo。</p></header>''' + "".join(cards) + "</html>", encoding="utf-8")
print(md_out)
print(html_out)
