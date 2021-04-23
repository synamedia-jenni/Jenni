import os
from unittest import mock

from jenni.steps.stashing import Step
from jenni.tests.unittestutils import *


class Tests(TestCase):
    def setUp(self):
        super().setUp()
        self.params = dict(
            choice="x",
            count=99,
            custom1="custom1-value",
            false_flag=False,
            true_flag=True,
            str="abc",
            validating_str="xxx",
            non_stored_password="yyy",
            text="hi\nthere",
        )

    def _run_fail(self, exception, regex, **kwargs):
        self.params.update(kwargs)
        with self.assertRaisesRegex(exception, regex):
            with setup_environment_vars(**self.params):
                self.run_job("params_job")

    def _run_pass(self, **kwargs):
        self.params.update(kwargs)
        with setup_environment_vars(**self.params):
            self.run_job("params_job")

    def test_correct_values(self):
        with setup_environment_vars(**self.params):
            self.run_job("params_job")

    def test_wrong_choice_value(self):
        self._run_fail(AssertionError, r"wrong choice value a", choice="a")

    def test_wrong_str_value(self):
        self._run_fail(AssertionError, r"wrong str value xyz", str="xyz")

    def test_wrong_validating_str_value(self):
        self._run_fail(AssertionError, r"wrong validating_str value 123", validating_str="123")

    def test_wrong_non_stored_password_value(self):
        self._run_fail(AssertionError, r"wrong non_stored_password value 123", non_stored_password="123")

    def test_wrong_text_value(self):
        self._run_fail(AssertionError, r"wrong text value good\nmorning", text="good\nmorning")

    def test_wrong_int_value(self):
        self._run_fail(AssertionError, r"wrong count value 999", count=999)

    def test_wrong_int_syntax(self):
        self._run_fail(
            SystemExit,
            r"Job parameter count has invalid integer value.*not-an-integer",
            count="not-an-integer",
        )

    def test_right_bool_true_values(self):
        for flag in ("TRUE", "True", "true", "YES", "Yes", "yes", "1"):
            self._run_pass(true_flag=flag)

    def test_right_bool_false_values(self):
        for flag in ("FALSE", "False", "false", "no", "No", "no", "0"):
            self._run_pass(false_flag=flag)

    def test_wrong_bool_true_flag_value(self):
        for flag in ("FALSE", "False", "false", "no", "No", "no", "0"):
            self._run_fail(AssertionError, r"wrong true_flag value False", true_flag=flag)

    def test_wrong_bool_false_flag_value(self):
        for flag in ("TRUE", "True", "true", "YES", "Yes", "yes", "1"):
            self._run_fail(AssertionError, r"wrong false_flag value True", false_flag=flag)

    def test_wrong_bool_syntax(self):
        self._run_fail(
            SystemExit,
            r"Job parameter true_flag has invalid value \(not-a-boolean\): expecting 1/0/yes/no/true/false",
            true_flag="not-a-boolean",
        )

    def test_missing_bool_value(self):
        self._run_fail(
            SystemExit,
            r"Parameter true_flag is undefined: missing environment variable \(true_flag\)",
            true_flag=None,
        )

    def test_missing_int_value(self):
        self._run_fail(
            SystemExit,
            r"Parameter count is undefined: missing environment variable \(count\)",
            count=None,
        )

    def test_missing_choice_value(self):
        self._run_fail(
            SystemExit,
            r"Parameter choice is undefined: missing environment variable \(choice\)",
            choice=None,
        )

    def test_seed(self):
        self.generate(
            # "params_job",
            contains=[
                """booleanParam('false_flag', true, '''A boolean param that should be false''')""",
                """booleanParam('true_flag', false, '''A boolean param that should be true''')""",
                """stringParam('count', '0', '''A int param that should be 99''')""",
                """stringParam('str', '''''', '''A string param that should be abc''')""",
                """textParam('text', '''''', '''A text param that should be hi\nthere''')""",
                """activeChoiceParam('custom1') {}""",
            ],
            not_contains=["cron"],
        )
