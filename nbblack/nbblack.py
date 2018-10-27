# -*- coding: utf-8 -*-
import black
import isort
import nbformat

setting_overrides = {
    "multi_line_output": 3,
    "include_trailing_comma": True,
    "force_grid_wrap": 0,
    "combine_as_imports": True,
    "line_length": 88,
}


def isort_cell(cell):
    cell.source = isort.SortImports(
        file_contents=cell.source, setting_overrides=setting_overrides
    ).output.strip()


def blacken_cell(cell):
    try:
        blackened = black.format_file_contents(cell.source, line_length=88, fast=True)
    except (SyntaxError, black.InvalidInput, black.NothingChanged):
        pass
    else:
        cell.source = blackened.strip()


def blacken_notebook_contents(source):
    notebook = nbformat.reads(source, as_version=4)

    for cell in notebook.cells:
        if cell.cell_type == "code":
            isort_cell(cell)
            blacken_cell(cell)

    return notebook
