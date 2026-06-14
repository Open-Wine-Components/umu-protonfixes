"""Game fix for Medal of Honor: Allied Assault War Chest"""

from protonfixes import util


def main() -> None:
    # Fix game not launching
    util.set_environment('MESA_EXTENSION_MAX_YEAR', '2002')
    util.set_environment('__GL_ExtensionStringVersion', '17700')
