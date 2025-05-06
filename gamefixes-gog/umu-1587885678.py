"""Game fix for Breath of Fire IV"""

from protonfixes import util


def main() -> None:
    """Load shipped dlls"""
    util.winedll_override('ddraw', util.OverrideOrder.NATIVE_BUILTIN)
    util.winedll_override('dinput', util.OverrideOrder.NATIVE_BUILTIN)
