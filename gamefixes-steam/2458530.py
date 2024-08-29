"""Game fix for Sanoba Witch FHD Edition"""

from protonfixes import util


def main():
    """
    Fixes in-game video playback for the intro and ending.
    """
    util.disable_protonmediaconverter()
