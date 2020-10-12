"""
addon_subcmd.py
------------.

General Addon Managing Utilities.
The functions below can be called via the `manim addon` subcommand.

"""
import os
import configparser
from ast import literal_eval
import pathlib
import csv

from .config_utils import _run_config, _paths_config_file, finalized_configs_dict
from ..utils.file_ops import guarantee_existence, open_file

from rich.console import Console
from rich.style import Style
from rich.errors import StyleSyntaxError
from rich.table import Table

__all__ = ["install", "list_addons","remove"]

ADDON_DIR = pathlib.Path("..") / ".." / "addons"

if not ADDON_DIR.exists():
    os.mkdir(ADDON_DIR)

console = Console()


def value_from_string(value):
    """Extracts the literal of proper datatype from a string.
    Parameters
    ----------
    value : :class:`str`
        The value to check get the literal from.

    Returns
    -------
    Union[:class:`str`, :class:`int`, :class:`bool`]
        Returns the literal of appropriate datatype.
    """
    try:
        value = literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    return value


def _is_expected_datatype(value, expected, style=False):
    """Checks whether `value` is the same datatype as `expected`,
    and checks if it is a valid `style` if `style` is true.

    Parameters
    ----------
    value : :class:`str`
        The string of the value to check (obtained from reading the user input).
    expected : :class:`str`
        The string of the literal datatype must be matched by `value`. Obtained from
        reading the cfg file.
    style : :class:`bool`, optional
        Whether or not to confirm if `value` is a style, by default False

    Returns
    -------
    :class:`bool`
        Whether or not `value` matches the datatype of `expected`.
    """
    value = value_from_string(value)
    expected = type(value_from_string(expected))

    return isinstance(value, expected) and (is_valid_style(value) if style else True)


def is_valid_style(style):
    """Checks whether the entered color is a valid color according to rich
    Parameters
    ----------
    style : :class:`str`
        The style to check whether it is valid.
    Returns
    -------
    Boolean
        Returns whether it is valid style or not according to rich.
    """
    try:
        Style.parse(style)
        return True
    except StyleSyntaxError:
        return False


def replace_keys(default):
    """Replaces _ to . and viceversa in a dictionary for rich
    Parameters
    ----------
    default : :class:`dict`
        The dictionary to check and replace
    Returns
    -------
    :class:`dict`
        The dictionary which is modified by replcaing _ with . and viceversa
    """
    for key in default:
        if "_" in key:
            temp = default[key]
            del default[key]
            key = key.replace("_", ".")
            default[key] = temp
        else:
            temp = default[key]
            del default[key]
            key = key.replace(".", "_")
            default[key] = temp
    return default


def install(repo_name: str, hostname: str = "github"):
    link_starter = (
        "https://github.com/"
        if hostname == "github"
        else "https://gitlab.com/"
        if hostname == "gitlab"
        else "https://bitbucket.org/"
        if hostname == "bitbucket"
        else hostname
    )
    split_repo_name = repo_name.split("/")

    user, repo = split_repo_name[0], split_repo_name[1]

    old_curr_dir = os.getcwd()

    os.chdir(ADDON_DIR)
    os.system(f"git clone {link_starter+repo_name}")

    cwd = pathlib.Path(".")

    cfg_file = cwd / repo / "manim.cfg"

    if not cfg_file.exists() or not ("is_addon=True" in open(cfg_file)):
        os.rmdir(cwd)

        raise FileNotFoundError(
            "The addon repo you specified does not have a manim.cfg file or is not an addon."
        )

    else:
        imports_file = pathlib.Path("..") / "__init__.py"

        with open(imports_file, "a") as _file:
            _file.append(f"from .addons.{repo} import *")

    console.print(
        f"Done! The objects in addon {repo} by {user} can now be accessed via manim"
    )

    _add_addon_to_database(repo, user, link_starter + repo_name)

    os.chdir(old_curr_dir)


def _add_addon_to_database(repo, creator, link):
    with open(ADDON_DIR / "addons.csv", "w") as _file:
        writer = csv.writer(_file)
        if _file.readlines() == []:
            writer.writerow(["Name", "Creator", "Link to repository"])

        writer.writerow([repo, creator, link])
    console.print(f"Addon {repo} added to database.")


def list_addons():
    with open(ADDON_DIR / "addons.csv", "r") as _file:
        reader = csv.reader(_file)

        table = Table()

        table.add_column("Name")
        table.add_column("Creator")
        table.add_column("Link to Repository")

        for row in reader:
            table.add_row(*row)

        console.print(table)


def remove(name: str):
    imports_file = pathlib.Path("..") / "__init__.py"

    with open(imports_file, "r+") as _file:
        lines = _file.readlines()

        lines.remove(f"from .addons.{name} import *")

        _file.seek(0)

        _file.writelines(lines)

    os.rmdir(ADDON_DIR / name)

    console.print(f"Addon {name} successfully removed.")
