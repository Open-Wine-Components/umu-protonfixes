"""Game fix for SP-Tushonka"""

from protonfixes import util

def main() -> None:
    # Required by commonly used mod launchers (e.g "SVM")
    util.protontricks('dotnetdesktop9')

    # Required to not crash on game launch ("BepInEx" hook)
    util.winedll_override('winhttp', util.OverrideOrder.NATIVE_BUILTIN)

    # Fixes "no keyboard input" issue on ALT-TAB / focus loss
    util.regedit_add(
        'HKEY_CURRENT_USER\\Software\\Wine\\X11 Driver',
        'UseTakeFocus',
        'REG_SZ',
        'N',
    )