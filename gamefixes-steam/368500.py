"""Game fix for Assassin's Creed: Syndicate"""

from protonfixes import util


def main() -> None:
    """Game ships with outdated UPlay launcher, which impedes normal initialization"""
    util.protontricks('ubisoftconnect')
    util.disable_nvapi()
