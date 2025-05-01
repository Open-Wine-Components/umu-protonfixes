"""Game fix for YOU and ME and HER: A Love Story"""

from protonfixes import util


def main() -> None:
    # Fixes audio not playing for in-game videos
    util.disable_protonmediaconverter()
