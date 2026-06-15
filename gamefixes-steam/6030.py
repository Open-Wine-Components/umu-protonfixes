"""Game fix for Star Wars Jedi Knight II: Jedi Outcast"""

from protonfixes import util


def early() ->  None:
    # Fix game not launching
    util.set_environment('PROTON_OLD_GL_STRING', '1')
