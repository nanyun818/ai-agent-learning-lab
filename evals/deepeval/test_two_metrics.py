"""Verify independent metric inputs and error accounting; no real judge calls."""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from lesson import OfflineJudge, make_metric, make_test
from two_metrics import coverage_metric, selected_cases, summary


class RecordingJudge(OfflineJudge):
    def __init__(self):
        self.prompts = []
        super().__init__()

    def generate(self, prompt, schema=None):
        self.prompts.append(prompt)
        return super().generate(prompt, schema)


class TwoMetricTests(unittest.TestCase):
    @patch("lesson.urlopen", side_effect=AssertionError("No network in offline check"))
    def test_metrics_see_their_intended_inputs(self, request):
        case = selected_cases("j05")[0]
        case["vars"]["context_text"] = "CONTEXT_VISIBILITY_SENTINEL"
        judge = RecordingJudge()
        for factory in (make_metric, coverage_metric):
            metric = factory(judge)
            metric.measure(make_test(case), _show_indicator=False)
        self.assertEqual(judge.calls, 2)
        self.assertIn("CONTEXT_VISIBILITY_SENTINEL", judge.prompts[0])
        self.assertNotIn("CONTEXT_VISIBILITY_SENTINEL", judge.prompts[1])
        self.assertNotIn("reference_judge_pass", "".join(judge.prompts))
        request.assert_not_called()

    def test_error_excluded_from_valid_verdict_count(self):
        data = {"planned_scores": 2, "requests_attempted": 2, "rows": [
            {"id": "j05", "metric": "evidence", "status": "graded", "pass": True, "reference_pass": True, "reason": "x"},
            {"id": "j05", "metric": "coverage", "status": "error", "error": "simulated timeout"},
        ]}
        output = io.StringIO()
        with redirect_stdout(output):
            summary(data)
        self.assertIn("有效维度判分 1/2", output.getvalue())
        self.assertIn("与建议一致 1/1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
