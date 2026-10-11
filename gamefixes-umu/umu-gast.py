"""Game fix for Gast: The greatest little ghost! (PC CD)"""

from protonfixes import util


def main() -> None:
    """Fix video playback"""
    util.protontricks('quartz')
