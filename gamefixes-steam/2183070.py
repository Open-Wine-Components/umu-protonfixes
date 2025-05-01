"""Game fix for Tokyo Necro"""

from protonfixes import util


def main() -> None:
    # Fixes audio not playing for in-game videos
    util.disable_protonmediaconverter()
