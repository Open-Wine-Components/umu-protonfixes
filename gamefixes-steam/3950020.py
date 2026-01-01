"""Game fix for Duet Night Abyss"""

from protonfixes import util


def main() -> None:
    """CEF tries to use dcomp by default which only has stubs, this triggers a fallback to a different backend"""
    util.winedll_override('dcomp', util.OverrideOrder.DISABLED)
