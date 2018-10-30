# -*- coding: utf-8 -*-
"""Console script for nbblack."""
import re
import shutil
import sys
from pathlib import Path

import click
import nbformat

from . import __version__
from .nbblack import blacken_notebook_contents
from .errors import NotPythonNotebookError

DEFAULT_INCLUDE = r"(\.ipynb$)"
DEFAULT_EXCLUDE = r"(\.git$|\.ipynb_checkpoints)"


def collect_sources(srcs, include, exclude):
    sources = set()
    for s in srcs:
        p = Path(s)
        if p.is_dir():
            sources.update(
                iter_files_in_dir(p, "/", include, exclude)
            )
        elif p.is_file():
            sources.add(p)

    return sources


def iter_files_in_dir(path, root, include, exclude):
    for s in path.iterdir():
        p = Path(s)
        normalized_path = "/" + p.resolve().relative_to(root).as_posix()

        if p.is_dir():
            normalized_path += "/"
        if exclude.search(normalized_path):
            continue
        if p.is_dir():
            yield from iter_files_in_dir(p, "/", include, exclude)
        elif p.is_file():
            if include.search(normalized_path):
                yield p
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted, "
        "silence those with 2>/dev/null."
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=(
        "Also emit messages to stderr about files that were not changed or were "
        "ignored due to --exclude=."
    ),
)
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
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
@click.option(
    "--include",
    type=str,
    default=DEFAULT_INCLUDE,
    help=(
        "A regular expression that matches files and directories that should be "
        "included on recursive searches.  An empty value means all files are "
        "included regardless of the name.  Use forward slashes for directories on "
        "all platforms (Windows, too).  Exclusions are calculated first, inclusions "
        "later."
    ),
    show_default=True,
)
@click.option(
    "--exclude",
    type=str,
    default=DEFAULT_EXCLUDE,
    help=(
        "A regular expression that matches files and directories that should be "
        "excluded on recursive searches.  An empty value means no paths are excluded. "
        "Use forward slashes for directories on all platforms (Windows, too).  "
        "Exclusions are calculated first, inclusions later."
    ),
    show_default=True,
)
@click.option("--collect-only", is_flag=True, help="Only collect notebooks, don't format them")
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, writable=True
    ),
)
@click.pass_context
def main(ctx, src, collect_only, in_place, include, exclude, quiet, verbose):
    try:
        include_regex = re.compile(include)
    except re.error:
        click.secho(f"Invalid regular expression for include given: {include!r}", fg="red", err=True)
        ctx.exit(1)
    try:
        exclude_regex = re.compile(exclude)
    except re.error:
        click.secho(f"Invalid regular expression for exclude given: {exclude!r}", fg="red", err=True)
        ctx.exit(1)

    backup_ext = None
    if in_place is not None and len(in_place) > 0:
        backup_ext = in_place

    notebooks = collect_sources(src, include_regex, exclude_regex)
    if len(notebooks) == 0:
        if verbose or not quiet:
            click.secho("No notebooks given. Nothing to do. 😴", err=True)
        ctx.exit(0)

    if collect_only:
        for notebook in notebooks:
            click.secho(notebook.as_posix(), bold=True, err=True)
        return ctx.exit(0)

    for notebook in notebooks:
        try:
            nb = blacken_notebook_contents(notebook.read())
        except NotPythonNotebookError:
            click.secho(
                "{0} does not appear to be a python notebook".format(notebook.name),
                fg="red",
                err=True,
            )
            return ctx.exit(1)

        if backup_ext:
            shutil.copy2(notebook.name, notebook.name + backup_ext)

        nbformat.write(nb, notebook.name)

    return ctx.exit(0)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
