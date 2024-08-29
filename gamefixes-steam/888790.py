"""Game fix for Sabbat of the Witch"""

from protonfixes import util


def main():
    """
    Fixes in-game video playback for the intro and ending.
    """
    util.disable_protonmediaconverter()
