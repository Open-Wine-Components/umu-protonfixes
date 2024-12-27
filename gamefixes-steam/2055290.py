"""Sonic Colors: Ultimate"""

from protonfixes import util


def main() -> None:
    """Black screen for some users unless deleting XDG_DATA_HOME variable"""
    util.del_environment('XDG_DATA_HOME')
