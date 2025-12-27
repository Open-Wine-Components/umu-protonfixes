"""Game fix for Ghost Recon WIldlands"""

from protonfixes import util


def main() -> None:
    """Game ships with outdated UPlay launcher, which impedes normal initialization"""
    util.protontricks('ubisoftconnect')
