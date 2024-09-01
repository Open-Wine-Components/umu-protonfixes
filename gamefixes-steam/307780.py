"""Game fix for Mortal Kombat X"""

from protonfixes import util


def main() -> None:
    # Fix pre-rendered cutscene playback
    util.protontricks('xact_x64')
