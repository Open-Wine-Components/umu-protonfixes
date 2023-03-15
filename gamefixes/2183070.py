""" Game fix for Tokyo Necro
"""

from protonfixes import util

def main():
    """ installs xact, disable ESYNC, disable FSYNC
    """

    # Fixes crash after typing then entering or clicking `search` within the game's terminal menu
    util.protontricks('xact')
    # Fixes hanging after typing then entering or clicking `search` within the game's terminal menu
    util.set_environment('PROTON_NO_ESYNC', '1')
    util.set_environment('PROTON_NO_FSYNC', '1')
