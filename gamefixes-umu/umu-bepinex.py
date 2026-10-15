"""BepInEx https://docs.bepinex.dev/articles/advanced/proton_wine.html"""

from protonfixes import util

def main() -> None:
    # corefonts needed for UI
    util.protontricks('corefonts')
    util.winedll_override('winhttp', util.OverrideOrder.NATIVE_BUILTIN)
