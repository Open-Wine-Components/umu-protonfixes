"""Duke Nukem: Manhattan Project - Enhanced Edition"""

from protonfixes import util


def main() -> None:
    util.winedll_override('d3d8', util.OverrideOrder.NATIVE_BUILTIN)
    util.protontricks('vcrun2019')
