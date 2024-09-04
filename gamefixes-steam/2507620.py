"""Game fix for The Quintessential Quintuplets - Five Memories Spent With You"""

from protonfixes import util


def main() -> None:
    """Install xact"""
    # Fixes audio not playing and some background music
    util.protontricks('xact')
