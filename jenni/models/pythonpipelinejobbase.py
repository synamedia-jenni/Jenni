import os

from .pipelinejobbase import PipelineJobBase

# See https://docs.python.org/3.6/library/abc.html
from abc import ABC, abstractmethod

from ..steps import Step


class PythonPipelineJobBase(PipelineJobBase, ABC):
    """
    Baseclass for jobs that are implemented using Python code.
    This is still very much a work in progress.

    :warning: Please see `Security <security.html>`_ for security concerns about the current implementation.
    """

    #: Provides access to Jenkins workflow (aka pipeline) steps.
    workflow = Step()

    @abstractmethod
    def run(self):
        """
        To be implemented by subclass
        """

    # Implement this method, we don't have to customise the initialisation,
    # since we require the run method to be implemented.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_script(self) -> str:
        root_folder = self.get_root_folder()
        with open(os.path.join(os.path.dirname(__file__), "run.groovy"), "rt") as fp:
            script = fp.read()

        pre, mid, post = script.split("//WRAP_INSIDE_NODE\n")
        mid = root_folder.pythonpipelinejob_inside_node_wrapper(self, mid)
        script = pre + mid + post
        script = self.get_root_folder().pythonpipelinejob_main_wrapper(self, script)
        return script
