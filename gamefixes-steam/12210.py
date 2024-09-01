"""Game fix for GTA IV"""

from protonfixes import util


def main() -> None:
    """installs wmp11"""
    # Fixes Independence FM user radio station
    util.protontricks('wmp11')
