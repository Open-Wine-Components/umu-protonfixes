"""Deus Ex: Invisible War"""

from protonfixes import util


def main() -> None:
    # Fix for extremely loud audio glitches when using Spy Drones
    util.protontricks('dsound')
