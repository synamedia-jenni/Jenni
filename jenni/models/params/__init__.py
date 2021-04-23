import os
from abc import abstractmethod, ABC
from collections.abc import Iterable
from typing import List, TYPE_CHECKING, Optional

from ...utils import quote3xs, quote_list, quote1s

if TYPE_CHECKING:
    from ..jobbase import JobBase


class ParamBase(ABC):
    # Allows control of parameter ordering. 0 is at the top, 100 at the bottom.
    MIN_ORDER = 0
    DEFAULT_ORDER = 50
    MAX_ORDER = 99

    def __init__(self, job: "jenni.models.jobbase.JobBase", name: str, description: str, order: int = DEFAULT_ORDER):
        self.job = job
        self.name = name
        self.description = description
        if order < ParamBase.MIN_ORDER or order > ParamBase.MAX_ORDER:
            raise SystemExit(
                f"Parameter {self.name} order ({order}) is outside allowable range {ParamBase.MIN_ORDER} - {ParamBase.MAX_ORDER} inclusive"
            )
        self.order = order
        self.initialised = False
        for param in job.parameters:
            if param.name == name:
                raise SystemExit(f"Job ({job}) already has a parameter called {self.name}")

    def __str__(self):
        s = f"{self.__class__.__name__}({self.name}: "
        if self.initialised:
            s += f"{self.value})"
        else:
            s += "<not-initialised>)"
        return s

    @abstractmethod
    def _set_value(self):
        ...

    def _get_value_from_environ(self) -> str:
        value = os.environ.get(self.name, None)
        if value is None:
            raise SystemExit(f"Parameter {self.name} is undefined: missing environment variable ({self.name})")
        return value

    def check_initialised(self):
        if not self.initialised:
            raise SystemExit(f"Job should have a parameter {self.name} but did not (missing environment parameter)")

    @abstractmethod
    def write_jobdsl(self, jobdsl: List[str]):
        ...


class BooleanParam(ParamBase):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
        default: bool = False,
    ):
        super().__init__(job, name, description, order)
        if not isinstance(default, bool):
            raise SystemExit(f"Boolean job parameter {self.name} default ({default}) should be bool instance")
        self.default = default
        self._value: bool = self.default

    def _set_value(self):
        s = self._get_value_from_environ()
        s_lc = s.lower()
        if s_lc in ("0", "no", "false"):
            self._value = False
        elif s_lc in ("1", "yes", "true"):
            self._value = True
        else:
            raise SystemExit(f"Job parameter {self.name} has invalid value ({s}): expecting 1/0/yes/no/true/false")
        self.initialised = True

    @property
    def value(self) -> bool:
        return self._value

    def write_jobdsl(self, jobdsl: List[str]):
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-booleanParam
        default = "true" if self.default else "false"
        dsl = f"booleanParam('{self.name}', {default}, {quote3xs(self.description)})"
        jobdsl.append(dsl)


class IntParam(ParamBase):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
        default: int = 0,
    ):
        super().__init__(job, name, description, order)
        if not isinstance(default, int):
            raise SystemExit(f"Integer job parameter {self.name} default ({default}) should be int instance")
        self.default = default
        self._value: int = default

    def _set_value(self):
        s = self._get_value_from_environ()
        try:
            self._value = int(s)
        except ValueError as ex:
            raise SystemExit(f"Job parameter {self.name} has invalid integer value ({s}): {ex}")
        self.initialised = True

    @property
    def value(self) -> int:
        return self._value

    def __int__(self) -> int:
        return self.value

    def write_jobdsl(self, jobdsl: List[str]):
        # there is no native integer param, so simulate via string
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-stringParam
        dsl = f"stringParam('{self.name}', '{self.default}', {quote3xs(self.description)})"
        jobdsl.append(dsl)


class StringParam(ParamBase):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
        default: str = "",
    ):
        super().__init__(job, name, description, order)
        if not isinstance(default, str):
            raise SystemExit(f"String job parameter {self.name} default ({default}) should be str instance")
        self.default: str = default
        self._value: str = default

    def _set_value(self):
        self._value = self._get_value_from_environ()
        self.initialised = True

    @property
    def value(self) -> str:
        self.check_initialised()
        return self._value

    def write_jobdsl(self, jobdsl: List[str]):
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-stringParam
        dsl = f"stringParam('{self.name}', {quote3xs(self.default)}, {quote3xs(self.description)})"
        jobdsl.append(dsl)


class ValidatingStringParam(ParamBase):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
        default: str = "",
        regex: str = "",
        validation_message: str = "",
    ):
        super().__init__(job, name, description, order)
        if not isinstance(default, str):
            raise SystemExit(f"String job parameter {self.name} default ({default}) should be str instance")
        if not isinstance(regex, str):
            raise SystemExit(f"String job parameter {self.name} regex ({regex}) should be str instance")
        if regex == "":
            raise SystemExit(f"String job parameter {self.name} regex ({regex}) should be non-empty")
        if not isinstance(validation_message, str):
            raise SystemExit(
                f"String job parameter {self.name} validation_message ({validation_message}) should be str instance"
            )
        if validation_message == "":
            raise SystemExit(
                f"String job parameter {self.name} validation_message ({validation_message}) should be non-empty"
            )
        self.default: str = default
        self.regex: str = regex
        self.validation_message: str = validation_message
        self._value: str = default

    def _set_value(self):
        self._value = self._get_value_from_environ()
        self.initialised = True

    @property
    def value(self) -> str:
        self.check_initialised()
        return self._value

    def write_jobdsl(self, jobdsl: List[str]):
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-stringParam
        dsl = f"""\
            configure {{ project ->
                project / 'properties' / 'hudson.model.ParametersDefinitionProperty' / 'parameterDefinitions' / 'hudson.plugins.validating__string__parameter.ValidatingStringParameterDefinition' {{
                    'name'({quote1s(self.name)})
                    'description'({quote3xs(self.description)})
                    'defaultValue'({quote3xs(self.default)})
                    'regex'({quote3xs(self.regex)})
                    'failedValidationMessage'({quote3xs(self.validation_message)})
                }}
            }}
        """
        jobdsl.append(dsl)


class NonStoredPasswordParam(ParamBase):
    def __init__(
        self,
        job: "JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
    ):
        super().__init__(job, name, description, order)
        self._value: str = ""

    def _set_value(self):
        self._value = self._get_value_from_environ()
        self.initialised = True

    @property
    def value(self) -> str:
        self.check_initialised()
        return self._value

    def write_jobdsl(self, jobdsl: List[str]):
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-nonStoredPasswordParam
        dsl = f"nonStoredPasswordParam('{self.name}', {quote3xs(self.description)})"
        jobdsl.append(dsl)


class CustomParam(StringParam):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str = "no-description",
        order: int = ParamBase.DEFAULT_ORDER,
        default: str = "",
        jobdsl: str = "",
    ):
        super().__init__(job, name, description, order, default)
        if jobdsl == "":
            raise SystemExit("CustomParam should have non-empty jobdsl")
        self.jobdsl = jobdsl

    def write_jobdsl(self, jobdsl: List[str]):
        jobdsl.append(self.jobdsl)


class TextParam(ParamBase):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
        default: str = "",
    ):
        super().__init__(job, name, description, order)
        if not isinstance(default, str):
            raise SystemExit(f"Type of text parameter default ({default}) should be str instance")
        self.default: str = default
        self._value: str = default

    def _set_value(self):
        self._value = self._get_value_from_environ()
        self.initialised = True

    @property
    def value(self) -> str:
        self.check_initialised()
        return self._value

    def write_jobdsl(self, jobdsl: List[str]):
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-textParam
        dsl = f"textParam('{self.name}', {quote3xs(self.default)}, {quote3xs(self.description)})"
        jobdsl.append(dsl)


# https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-choiceParam
class ChoiceParam(ParamBase):
    def __init__(
        self,
        job: "jenni.models.jobbase.JobBase",
        name: str,
        description: str,
        order: int = ParamBase.DEFAULT_ORDER,
        options: List[str] = [],
    ):
        super().__init__(job, name, description, order)
        if not isinstance(options, Iterable):
            raise SystemExit(
                f"Choice job parameter {self.name} options should be a List or other Iterable instance: {options}"
            )
        if not options:
            raise SystemExit(
                f"Choice job parameter {self.name} options should be a non-empty List or other Iterable instance: {options}"
            )
        for option in options:
            if not isinstance(option, str):
                raise SystemExit(f"Choice job parameter {self.name} options should be str instances: {option}")
        self.options = options
        self._value: Optional[str] = None

    def _set_value(self):
        self._value = self._get_value_from_environ()
        if self._value not in self.options:
            raise SystemExit(f"Value ({self._value}) of choices parameter ({self.name}) is not one of its options")
        self.initialised = True

    @property
    def value(self) -> Optional[str]:
        self.check_initialised()
        return self._value

    def write_jobdsl(self, jobdsl: List[str]):
        # https://jenkinsci.github.io/job-dsl-plugin/#path/javaposse.jobdsl.dsl.jobs.WorkflowJob.parameters-choiceParam
        dsl = f"choiceParam('{self.name}', {quote_list(self.options)}, {quote3xs(self.description)})"
        jobdsl.append(dsl)
