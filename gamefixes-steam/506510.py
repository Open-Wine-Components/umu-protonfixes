"""Shadows of Adam"""

from protonfixes import util


def main() -> None:
    """Fixes game getting stuck on a white screen."""
    util.winedll_override('dcomp', util.OverrideOrder.DISABLED)
