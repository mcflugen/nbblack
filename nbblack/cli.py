# -*- coding: utf-8 -*-
"""Console script for nbblack."""
import shutil
import sys

import click
import nbformat

from .nbblack import blacken_notebook_contents
from . import __version__

@click.command()
@click.version_option(version=__version__)
@click.option(
    "--in-place",
    help=(
        "Edit files in-place, saving backups with the specified extension.  "
        "If a zero-length extension is given, no backup will be saved.  It "
        "is not recommended to give a zero-length extension when in-place "
        "editing files, as you risk corruption or partial content in "
        "situations where disk space is exhausted, etc."
    ),
)
@click.argument("notebook", type=click.File(mode="r"))
def main(notebook, in_place):
    backup_ext = None
    if in_place is not None and len(in_place) > 0:
        backup_ext = in_place

    nb = blacken_notebook_contents(notebook.read())
    if not in_place:
        dest = sys.stdout
    else:
        dest = notebook.name
    if backup_ext:
        shutil.copy2(notebook.name, notebook.name + backup_ext)

    nbformat.write(nb, dest)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
