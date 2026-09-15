"""Game fix for Tom Clancy's Rainbow Six"""

from protonfixes import util

def main() -> None:
    # Fix game not launching
    # Requires setting the Windows version to Windows 95 or 98. Winetricks doesn't support setting this on a 64-bit prefix but this can be worked around by editing the registry directly
    util.regedit_add(
        'HKEY_CURRENT_USER\\Software\\Wine',
        'Version',
        'REG_SZ',
        'win98',
    )
    # Fix in-game music not playing on GOG version
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
