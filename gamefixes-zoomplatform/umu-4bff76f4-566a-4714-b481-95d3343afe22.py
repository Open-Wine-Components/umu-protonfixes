"""Incoming Trilogy"""

from protonfixes import util


def main() -> None:
    util.winedll_override('d3d8', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('ddraw', util.OverrideOrder.BUILTIN)
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
