from abc import ABC
from typing import List

from jenni.models.itembase import ItemBase
from jenni.models.params import ParamBase


class JobBase(ItemBase, ABC):
    """
    Base class for all types of jobs.
    """

    @property
    def parameters(self) -> List["jenni.models.params.ParamBase"]:
        """
        :return: list of ParamBase instances
        """
        return [value for value in self.__dict__.values() if isinstance(value, ParamBase)]

    def has_parameter(self, name: str) -> bool:
        """
        :return: True if job has specified parameter.
        """
        for value in self.__dict__.values():
            if isinstance(value, ParamBase) and value.name == name:
                return True
        return False

    def get_parameter(self, name: str, exception_if_not_found=True) -> "ParamBase":
        """
        :return: ParamBase instance, or None (if exception_if_not_found is False)
        """
        for value in self.__dict__.values():
            if isinstance(value, ParamBase) and value.name == name:
                return value
        if exception_if_not_found:
            raise LookupError("No parameter with name " + name)
        return None
