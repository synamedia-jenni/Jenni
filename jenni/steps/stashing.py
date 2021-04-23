from abc import ABC

from jenni.stepbase import StepBase
from jenni.utils import quote3xs


class Step(StepBase, ABC):
    def stash(self, name: str, includes: str):
        code = "stash(name:" + quote3xs(name) + ", includes:" + quote3xs(includes) + ")"
        return self.execute_groovy(code)

    def unstash(self, name: str):
        code = "unstash(name:" + quote3xs(name) + ")"
        return self.execute_groovy(code)
