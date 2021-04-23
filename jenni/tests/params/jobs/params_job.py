import jenni


class Job(jenni.models.PythonPipelineJobBase):
    def __init__(self):
        super().__init__(description="My params job", title="A Job")
        self.choice = jenni.models.params.ChoiceParam(
            self, name="choice", options=["a", "b", "x", "y"], description="A choice param that should be x"
        )
        self.count = jenni.models.params.IntParam(self, "count", "A int param that should be 99")
        self.str = jenni.models.params.StringParam(self, "str", "A string param that should be abc")
        self.non_stored_password = jenni.models.params.NonStoredPasswordParam(
            self, "non_stored_password", "A non-stored string param that cannot have a default value"
        )
        self.validating_str = jenni.models.params.ValidatingStringParam(
            self,
            "validating_str",
            "A validating string param that should be xxx",
            regex=".*xxx.*",
            default="xxx",
            validation_message="wrong!",
        )
        self.text = jenni.models.params.TextParam(self, "text", "A text param that should be hi\nthere")
        self.true_flag = jenni.models.params.BooleanParam(
            self, "true_flag", "A boolean param that should be true", default=False
        )
        self.false_flag = jenni.models.params.BooleanParam(
            self, "false_flag", "A boolean param that should be false", default=True
        )
        self.custom1 = jenni.models.params.CustomParam(
            self,
            "custom1",
            jobdsl="activeChoiceParam('custom1') {}",
            default="custom1-default",
        )

    def run(self):
        print("hello")
        assert self.choice.value == "x", f"wrong choice value {self.choice.value}"
        assert self.count.value == 99, f"wrong count value {self.count.value}"
        assert self.str.value == "abc", f"wrong str value {self.str.value}"
        assert self.validating_str.value == "xxx", f"wrong validating_str value {self.validating_str.value}"
        assert (
            self.non_stored_password.value == "yyy"
        ), f"wrong non_stored_password value {self.non_stored_password.value}"
        assert self.custom1.value == "custom1-value", f"wrong custom1 value {self.custom1.value}"
        assert self.text.value == "hi\nthere", f"wrong text value {self.text.value}"
        assert self.true_flag.value, f"wrong true_flag value {self.true_flag.value}"
        assert not self.false_flag.value, f"wrong false_flag value {self.false_flag.value}"
