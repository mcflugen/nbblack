# -*- coding: utf-8 -*-
import re
import black
import isort
import nbformat

from .errors import NotPythonNotebookError

_ISORT_SETTINGS = {
    "multi_line_output": 3,
    "include_trailing_comma": True,
    "force_grid_wrap": 0,
    "combine_as_imports": True,
    "line_length": 88,
}
_BLACK_SETTINGS = {"line_length": 88, "fast": True}

_MAGIC_LINE_REGEX = re.compile(r"^(?=([ \t]*[!%].*$))", re.MULTILINE)
_REMOVE_ME = "# temporarily commented out by nbblack #"


def comment_magic(contents):
    return re.sub(_MAGIC_LINE_REGEX, _REMOVE_ME, contents)


def uncomment_magic(contents):
    return re.sub("^{0}".format(_REMOVE_ME), "", contents, re.MULTILINE)


def isort_cell(cell):
    cell.source = isort.SortImports(
        file_contents=cell.source, setting_overrides=_ISORT_SETTINGS
    ).output.strip()


def blacken_cell(cell):
    cell.source = comment_magic(cell.source)
    try:
        blackened = black.format_file_contents(cell.source, **_BLACK_SETTINGS)
    except (SyntaxError, black.NothingChanged):
        pass
    else:
        cell.source = blackened.strip()
    cell.source = uncomment_magic(cell.source)


def blacken_notebook_contents(source):
    notebook = nbformat.reads(source, as_version=4)

    if not is_python_notebook(notebook):
        raise NotPythonNotebookError()

    for cell in notebook.cells:
        if cell.cell_type == "code":
            isort_cell(cell)
            blacken_cell(cell)

    return notebook


def is_python_notebook(notebook):
    try:
        return notebook.metadata.kernelspec["language"] == "python"
    except KeyError:
        return False
