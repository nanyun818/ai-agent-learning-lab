"""Exercise actual SDK nesting in memory, and score linkage without network."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

from langfuse import Langfuse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from trace_demo import build_payload, emit_trace, credentials, TRACE_NAME


class TraceDemoTests(unittest.TestCase):
    def test_actual_sdk_tree_and_score_links_without_network(self):
        exporter = InMemorySpanExporter()
        client = Langfuse(public_key="pk-lf-offline-" + uuid.uuid4().hex, secret_key="offline-placeholder",
                          base_url="http://127.0.0.1:9", tracer_provider=TracerProvider(), span_exporter=exporter)
        payload = build_payload()
        try:
            with patch.object(client, "create_score") as scores:
                trace_id = emit_trace(client, payload)
                client.flush()
                spans = exporter.get_finished_spans()
                self.assertEqual({span.name for span in spans}, {TRACE_NAME, "prepare-case-display", "attach-existing-scores"})
                root = next(span for span in spans if span.name == TRACE_NAME)
                self.assertTrue(all(span.parent.span_id == root.context.span_id for span in spans if span is not root))
                self.assertTrue(all(format(span.context.trace_id, "032x") == trace_id for span in spans))
                self.assertEqual(scores.call_count, 2)
                for call in scores.call_args_list:
                    self.assertEqual(call.kwargs["trace_id"], trace_id)
                    self.assertIn(call.kwargs["value"], (0.0, 1.0))
                self.assertFalse(any("generation" in span.name for span in spans))
        finally:
            client.shutdown()

    def test_invalid_report_not_imported_as_score(self):
        from trace_demo import ROOT
        paths = list((ROOT.parent / "deepeval" / "results").glob("dimensions-*.json"))
        source = json.loads(max(paths, key=lambda p: p.stat().st_mtime).read_text())
        next(row for row in source["rows"] if row["id"] == "j05")["status"] = "error"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_payload(path)

    @patch.dict(os.environ, {"LANGFUSE_PUBLIC_KEY": "", "LANGFUSE_SECRET_KEY": "", "LANGFUSE_BASE_URL": ""})
    @patch("trace_demo.sys.stdin.isatty", return_value=False)
    def test_missing_credentials_are_local_error(self, terminal):
        with self.assertRaises(ValueError):
            credentials()

    @patch.dict(os.environ, {"LANGFUSE_PUBLIC_KEY": "", "LANGFUSE_SECRET_KEY": "", "LANGFUSE_BASE_URL": ""})
    @patch("trace_demo.sys.stdin.isatty", return_value=True)
    @patch("trace_demo.input", return_value="")
    @patch("trace_demo.getpass", side_effect=["pk-lf-example", "sk-lf-example"])
    def test_interactive_input_stays_in_memory(self, hidden, prompt, terminal):
        self.assertEqual(credentials(), ("pk-lf-example", "sk-lf-example", "https://cloud.langfuse.com"))
        self.assertEqual(os.environ["LANGFUSE_SECRET_KEY"], "")


if __name__ == "__main__":
    unittest.main()
