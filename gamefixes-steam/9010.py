"""Game fix for Return to Castle Wolfenstein"""

from protonfixes import util


def main() -> None:
    # Fix game not launching
    util.set_environment('MESA_EXTENSION_MAX_YEAR', '2003')
    util.set_environment('__GL_ExtensionStringVersion', '17700')
