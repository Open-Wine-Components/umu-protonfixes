"""Game fix for Quake II (Original)"""

from protonfixes import util


def main() -> None:
    # Fix crash at startup when using OpenGL
    util.set_environment('MESA_EXTENSION_MAX_YEAR', '2003')
    util.set_environment('__GL_ExtensionStringVersion', '17700')
	# Fix in-game music not playing
    util.winedll_override('winmm', util.OverrideOrder.NATIVE_BUILTIN)
