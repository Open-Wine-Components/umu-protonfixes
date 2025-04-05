"""The Wheel of Time"""

from protonfixes import util


def main() -> None:
    util.winedll_override('ddraw', util.OverrideOrder.NATIVE_BUILTIN)  # GOG's dxcfg
