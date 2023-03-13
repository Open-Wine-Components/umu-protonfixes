""" Game fix for Tokyo Necro
"""

from protonfixes import util

def main():
    """ installs xact
    """

    # Fixes launch after typing then entering `search` within the game's terminal menu
    util.protontricks('xact')
