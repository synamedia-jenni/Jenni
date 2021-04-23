import jenni
from jenni.tests.unittestutils import RootFolder
from jenni.models import FolderBase


class Folder(RootFolder):
    def yield_items(self, module_name_to_load: str = ""):
        yield from super().yield_items(module_name_to_load)
        yield from self.yield_sub_item("generated_subfolder0", SubFolder)
        for name in ("generated_job0", "generated_job1"):
            yield from self.yield_sub_item(name, GeneratedJob)


class SubFolder(FolderBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def yield_items(self, module_name_to_load: str = ""):
        yield from super().yield_items(module_name_to_load)
        yield from self.yield_sub_item("generated_subjob0", GeneratedJob)


class GeneratedJob(jenni.models.GroovyJobBase):
    def __init__(self):
        super().__init__()
        self.code(f"echo 'hello from {self.name}';")
        self.code(f"echo 'I was defined at {self.__class__.__file__}';")
