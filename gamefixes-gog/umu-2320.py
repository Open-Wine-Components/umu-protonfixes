"""Game fix for Quake II (Original)"""

from protonfixes import util


def main() -> None:
    # Fix crash at startup when using OpenGL
    util.set_environment('PROTON_OLD_GL_STRING', '1')
	# Fix in-game music not playing
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
