from jenni import stepserver
from . import (
    archiveArtifacts,
    build,
    sh,
    stashing,
)


class Step(
    archiveArtifacts.Step,
    build.Step,
    sh.Step,
    stashing.Step,
):
    def execute_groovy(self, code: str):
        return stepserver.execute_groovy(code)
