"""Game fix for Quake II (Original)"""

from protonfixes import util


def early() -> None:
    # Fix game not launching when using OpenGL
    util.set_environment('PROTON_OLD_GL_STRING', '1')

def main() -> None:
	# Fix in-game music not playing on GOG version
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
