"""Game fix for Soldier of Fortune: Platinum Edition"""

from protonfixes import util


def early() ->  None:
    # Fix game not launching
    util.set_environment('PROTON_OLD_GL_STRING', '1')
