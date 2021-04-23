from abc import ABC, abstractmethod


class StepBase(ABC):
    @abstractmethod
    def execute_groovy(self, code: str):
        raise NotImplementedError()
