""" Game fix for YOU and ME and HER: A Love Story
"""

from protonfixes import util

def main():
    """ installs xact, disable ESYNC, disable FSYNC
    """

    # Fixes the game from crashing or hanging during intro
    util.protontricks('xact')
    util.set_environment('PROTON_NO_ESYNC', '1')
    util.set_environment('PROTON_NO_FSYNC', '1')
