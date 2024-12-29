"""Game fix for SpellForce"""

from protonfixes import util


def main() -> None:
    """Needs DirectPlay for multiplayer functionality"""
    util.protontricks('directplay')
