import inspect
import logging
import os
import sys
from abc import ABC, abstractmethod
from importlib import import_module
from io import TextIOWrapper
from pathlib import PurePosixPath
from types import ModuleType
from typing import Dict, Optional, List

import jenni

NO_DEFAULT = object()
item_by_jenkins_path: Dict[str, "jenni.models.itembase.ItemBase"] = dict()
item_by_module: Dict[str, "jenni.models.itembase.ItemBase"] = dict()
config_dir: str = ""  # set from instance.py


def reset():
    item_by_jenkins_path.clear()
    item_by_module.clear()


class ItemBase(ABC):
    @abstractmethod
    def __init__(self, description: str = "", name: str = "", title: str = "", skip_seed: bool = False, url: str = ""):
        """

        :param description: descriptive text shown in Jenkins for this item
        :param name: defaults to the name of the file or folder
        :param title: optional title of the item (defaults to the name of the item)
        :param skip_seed: if set to True, then do not seed this item in Jenkins
        :param url: URL to the job/folder. Must end with slash. Normally auto-calculated, unless it is the root folder.
        """
        self.parent: Optional["jenni.models.FolderBase"] = None
        self.children: List["ItemBase"] = []
        self.description: str = description
        self.title: str = title
        self.jenkins_path: str = ""
        self.skip_seed = skip_seed

        module_name = self.__module__
        if not (module_name.startswith("jobs.") or module_name == "jobs"):
            raise SystemExit(f"module name ({module_name}) should be 'jobs' or start with 'jobs.'")
        if module_name in item_by_module:
            raise SystemExit(f"Can only have one item per module: module = {module_name}")
        item_by_module[module_name] = self
        module = sys.modules[self.__module__]
        self.parent = getattr(module, "__parent_item__", None)
        if module_name == "jobs":
            self.name = ""
            self.item_path = PurePosixPath("jobs")
            self.jenkins_path = self.name
        else:
            self.item_path = PurePosixPath(self.parent.item_path) / module.__item_name__
            if name:
                self.name = name
            else:
                self.name = module.__item_name__
            if self.parent.jenkins_path:
                self.jenkins_path = self.parent.jenkins_path + "/" + self.name
            else:
                self.jenkins_path = self.name
        item_by_jenkins_path[self.jenkins_path] = self

        if self.parent is None:
            if not url:
                raise SystemExit(f"{self} should have non-empty url")
            if not url.endswith("/"):
                raise SystemExit(f"{self} should have non-empty url ending with a slash")
            self.url = url
        else:
            self.url = f"{self.parent.url}job/{self.name}/"
            self.parent.children.append(self)

        self.__initialized = True
        logging.debug(f" => {self}")
        if self.parent is not None and (self.parent.get_sub_item(self.name) is not self):
            raise SystemExit(f"parent-child relationship bug: {self}")

    def get_sub_item(self, sub_item_path: str) -> "ItemBase":
        if self.jenkins_path:
            return item_by_jenkins_path[f"{self.jenkins_path}/{sub_item_path}"]
        else:
            return item_by_jenkins_path[sub_item_path]

    @abstractmethod
    def write_jobdsl(self, fp: TextIOWrapper):
        pass

    def configure(self):
        """
        Optional, can be overridden in subclass.
        """
        pass

    def get_root_folder(self) -> "jenni.models.RootFolderBase":
        result = self
        for i in range(100):  # infinite recursion prevention
            if result.parent:
                result = result.parent
            else:
                return result
        else:
            raise Exception(f"Infinite parent chain, or too deeply nested: {self}")

    def __str__(self):
        return f"""{self.__class__.__name__}""" f"""({getattr(self, "jenkins_path", "<missing:jenkins_path")})"""

    def lookup_relative_filename(self, filename: str) -> str:
        """
        Return path to file.

        * If the filename starts with "/", it is relative to the config directory of the jenni seed command.
        * Otherwise the filename is relative to the directory containing the file defining the calling Job or Folder.

        :param filename: filename spec

        :return: full path to the file.
        """
        if filename.startswith("/"):
            return os.path.join(config_dir, filename[1:])
        dirname = os.path.dirname(sys.modules[self.__module__].__file__)
        return os.path.join(dirname, filename)

    def yield_sub_item(self, name, base_class, filename=None, parent=None, **kwargs):
        """
        Use this to dynamically create a Job or Folder instance. Specifically, it:

        * creates a new module containing a new class (named Job or Folder)
        * instances this class
        * calls yield_items on the instance.

        Example usage: yield from self.yield_sub_item("fast_track", MyTrack)

        :param name: the name of the module, relative to its parent.

        :param base_class: the base class of the created class

        :param filename: defaults to the filename of the calling function.

        :param parent: defaults to self.

        :param kwargs: additional arguments for base_class constructor

        :return: nothing. It uses yield instead.
        """
        from jenni.models.jobbase import JobBase
        from jenni.models import FolderBase

        if issubclass(base_class, JobBase):
            class_name = "Job"
        elif issubclass(base_class, FolderBase):
            class_name = "Folder"
        else:
            raise SystemExit(f"Invalid base class ({base_class}): should be subclass of JobBase or FolderBase")

        if parent is None:
            parent = self
        if filename is None:
            frame = inspect.currentframe()
            caller = frame.f_back
            filename = caller.f_code.co_filename
        if parent.__class__.__module__ != "jobs" and not parent.__class__.__module__.startswith("jobs."):
            raise SystemExit(
                f"parent.__class__.__module__ is not jobs or starting with jobs.: {parent.__class__.__module__}"
            )
        new_module_name = f"{parent.__class__.__module__}.{name}"
        module = ModuleType(new_module_name)
        module.__file__ = filename
        module.__item_name__ = name
        module.__parent_item__ = parent
        module.is_dynamically_generated = True
        sys.modules[new_module_name] = module
        new_cls = module.__dict__[class_name] = type(
            class_name,
            (base_class,),
            # class_name, (base_class, *base_class.__bases__),
            dict(__module__=new_module_name, __file__=filename),
        )
        item: ItemBase = new_cls(**kwargs)
        from jenni.models.jobbase import JobBase

        # from jenni.models.folderbase import FolderBase
        if isinstance(item, JobBase):
            item.parent.add_new_job(item)
        else:  # assumed to be a folder
            item.parent.add_new_folder(item)
        yield from item.parent.yield_items_pre_sub_item(item)
        yield from item.yield_items()
        yield from item.parent.yield_items_post_sub_item(item)
        item.parent.sub_item_completed_handler(item)

    def yield_items(self, module_name_to_load: str = ""):
        yield self

    def post_yield_handler(self):
        """Called bottom-up after all items have been yielded"""
        pass
