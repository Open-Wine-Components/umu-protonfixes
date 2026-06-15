"""Game fix for Soldier of Fortune II: Double Helix - Gold Edition"""

from protonfixes import util


def early() -> None:
    # Fix display issues
    util.set_environment('PROTON_OLD_GL_STRING', '1')
