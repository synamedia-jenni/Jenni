import jenni


class Folder(jenni.models.FolderBase):
    def __init__(self):
        super().__init__(description="This is folder1")
