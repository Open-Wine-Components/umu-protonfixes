"""Game fix for Star Wars Jedi Knight: Jedi Academy"""

from protonfixes import util


def early() ->  None:
    # Fix game not launching
    util.set_environment('PROTON_OLD_GL_STRING', '1')
