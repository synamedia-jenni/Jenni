from abc import ABC, abstractmethod
from io import TextIOWrapper

from jenni.models import PythonPipelineJobBase
from jenni.models.folderbase import FolderBase


class RootFolderBase(FolderBase, ABC):
    """
    Represents the pre-existing root folder in Jenkins below which jobs/folders are created.
    Has an empty name.
    """

    def __init__(self, url: str, **kwargs):
        """
        :param url: URL to the (possibly toplevel) Folder on the Jenkins server that this class represents.

        :param kwargs: optional arguments. Passed through to :class:`jenni.models.FolderBase` :func:`~jenni.models.FolderBase.__init__`.
        """
        super().__init__(name="", url=url, **kwargs)
        self.skip_seed = True

    def write_jobdsl(self, fp: TextIOWrapper):
        """
        Root folder already exists on the Jenkins server, so this is a no-op.
        """
        pass

    def pythonpipelinejob_main_wrapper(self, job: PythonPipelineJobBase, groovy_code: str) -> str:
        return groovy_code

    @abstractmethod
    def pythonpipelinejob_inside_node_wrapper(self, job: PythonPipelineJobBase, groovy_code: str) -> str:
        """
        Ensures appropriate code is executed around all code inside the node step.
        :param job:
        :param groovy_code:
        :return: groovy_code with preamble and postamble code
        """
        raise NotImplementedError()
