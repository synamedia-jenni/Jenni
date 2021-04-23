import logging
import os
import re
from typing import List

from jenni.models import PipelineJobBase
from jenni.utils import *


class GroovyJobBase(PipelineJobBase):
    """
    Baseclass for jobs that are implemented using Groovy pipeline scripts (https://www.jenkins.io/doc/book/pipeline/#scripted-pipeline-fundamentals).
    """

    _CODE_REPLACEMENT_REGEX = re.compile(r"""\{python\((?P<quotes>['"]{1,3})(.*?)(?P=quotes)\)\}""")

    def __init__(self, **kwargs):
        """
        :param kwargs: optional arguments. Passed through to :class:`~jenni.models.PipelineJobBase` :func:`~jenni.models.PipelineJobBase.__init__`.
        """
        super().__init__(**kwargs)

        #: a list of tuples, each either:
        #:
        #: * ``("include", "filename")`
        #: * ``("text", "groovy code...")``
        self._script_specs = []

    def include(self, filename: str):
        """
        Include the specified file (normally Groovy scripted pipeline code) into the job.

        Contents is checked for occurances of ``{python('''<code>''')}`` strings, and replaced with the result of executing ``<code>``.
        Instead of 3 single quotes, 3 double, or 1 single/double quote can be used.

        :param filename: See :func:`~jenni.models.itembase.ItemBase.lookup_relative_filename`
            for how a file may be found.
        """
        if not os.path.exists(self.lookup_relative_filename(filename)):
            raise FileNotFoundError(f"Cannot find included file ({filename})")
        self._script_specs.append(("include", filename))

    def include_first(self, filenames: List[str]):
        """
        Include the first found amongst the specified files
        (normally Groovy scripted pipeline code) into the job.

        See :func:`include` for ``{python('''<code>''')}`` replacements.

        :param filenames: See :func:`~jenni.models.itembase.ItemBase.lookup_relative_filename`
            for how each file may be found.
        """
        for filename in filenames:
            if os.path.exists(self.lookup_relative_filename(filename)):
                self.include(filename)
                return
        raise Exception(f"Cannot find any of the list of files to include the first one found of: ({filenames})")

    def code(self, code: str):
        """
        Include the specified text (normally Groovy scripted pipeline code) into the job.

        See :func:`include` for ``{python('''<code>''')}`` replacements.

        :param code: literal text to be inserted into the job pipeline script.
        """
        self._script_specs.append(("text", code))

    def get_file_contents(self, filename: str) -> str:
        """
        Return the contents of the file.

        No replacements are done like in the :func:`include` method.

        :param filename: See :func:`~jenni.models.itembase.ItemBase.lookup_relative_filename`
            for how the file may be found.
        """
        with open(self.lookup_relative_filename(filename)) as fp:
            return fp.read()

    def _get_script(self) -> str:
        snippets = []
        for spec in self._script_specs:
            if spec[0] == "text":
                self._append_code("text", tidy_text(spec[1]), snippets)
            elif spec[0] == "include":
                snippets.append(f"\n// scriptFile: {spec[1]}")
                self._append_code(spec[1], self.get_file_contents(spec[1]), snippets)
            else:
                raise Exception(f"Unknown script spec (bug?): {spec}")
        return "\n".join(snippets).strip()

    def _append_code(self, source, code, snippets):
        def replacer(matchobj):
            py_code = matchobj.group(2)
            # logging.debug(f"Replacing {py_code} by ...")
            # Adding nosec tag to suppress bandit raising
            # >> Issue: [B307:blacklist] Use of possibly insecure function - consider using safer ast.literal_eval.
            # We deem this safe because the input being processed are files under our control.
            result = eval(py_code, globals(), dict(self=self))  # nosec
            # logging.debug(f"... by {result}")
            return result

        try:
            code = self._CODE_REPLACEMENT_REGEX.sub(replacer, code)
            snippets.append(code)
        except Exception as ex:
            logging.error(f"{source}: {ex}")
            raise ex
