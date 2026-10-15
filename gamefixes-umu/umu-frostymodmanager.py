"""FrostyModManager linux fork https://github.com/maniman303/FrostyToolsuite"""

from protonfixes import util

def main() -> None:
    # https://www.nexusmods.com/masseffectandromeda/mods/1190
    util.winedll_override('dinput8', util.OverrideOrder.NATIVE_BUILTIN)
    # is required in some versions
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
