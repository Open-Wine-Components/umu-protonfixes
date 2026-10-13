"""MelonLoader https://melonwiki.xyz/#/?id=requirements"""

from protonfixes import util

def main() -> None:
    # dotnetdesktop6 needed for il2cpp games
    util.protontricks('dotnetdesktop6')
    util.winedll_override('version', util.OverrideOrder.NATIVE_BUILTIN)
