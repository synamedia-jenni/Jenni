from abc import ABC
from typing import List, Union

from jenni.stepbase import StepBase
from jenni.utils import bool2groovy, quote1or3xs


class Step(StepBase, ABC):
    """
    https://www.jenkins.io/doc/pipeline/steps/core/#archiveartifacts-archive-the-artifacts
    """

    # noinspection PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming
    def archiveArtifacts(
        self,
        artifacts: Union[str, List[str]],
        allowEmptyArchive=False,
        caseSensitive=True,
        defaultExcludes=True,
        excludes="",
        fingerprint=True,  # TODO correct default?
        onlyIfSuccessful=False,
    ):
        if not isinstance(artifacts, str):
            artifacts = ",".join(artifacts)
        code = (
            "archiveArtifacts("
            + f"{quote1or3xs(artifacts)},"
            + f"allowEmptyArchive:{bool2groovy(allowEmptyArchive)},"
            + f"caseSensitive:{bool2groovy(caseSensitive)},"
            + f"defaultExcludes:{bool2groovy(defaultExcludes)},"
            + f"excludes:{quote1or3xs(excludes)},"
            + f"fingerprint:{bool2groovy(fingerprint)},"
            + f"onlyIfSuccessful:{bool2groovy(onlyIfSuccessful)},"
            + ")"
        )
        return self.execute_groovy(code)
