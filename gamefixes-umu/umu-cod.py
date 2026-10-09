"""Game fix for Call of Duty (2003)"""

from protonfixes import util


def main() -> None:
    # Fix game crashing on launch due to long OpenGL extension string
    util.set_environment('MESA_EXTENSION_MAX_YEAR', '2003')
    util.set_environment('__GL_ExtensionStringVersion', '17700')
