import jenni
from jenni.models import FolderBase


class Job(jenni.models.PythonPipelineJobBase):
    def __init__(self):
        super().__init__(description="this is job1")

    def run(self):
        print(f"hello from {self.name}")
        assert self.name == "job1"

        folder: FolderBase = self.parent
        assert folder.name == "folder1"

        root_folder: FolderBase = folder.parent
        assert root_folder.name == ""
        assert root_folder.parent is None
