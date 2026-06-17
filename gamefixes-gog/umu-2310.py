"""Game fix for Quake"""

from protonfixes import util


def early() -> None:
    # Fix game not launching when using GLQuake
    util.set_environment('PROTON_OLD_GL_STRING', '1')


def main() -> None:
    # Due to legal issues the GOG version doesn't include the in-game music for WinQuake and GLQuake, but the dll used to achieve this is installed with the game
    # This dll override allows a user to have in-game music if they add their own .ogg files to the "MUSIC" folder and rename "_winmm.dll" to "winmm.dll"
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
