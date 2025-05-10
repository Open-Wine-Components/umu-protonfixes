"""Game fix for Mashed(281280)"""

from protonfixes import util


def main() -> None:
    """Mashed needs win xp otherwise cars may fall through the ground"""
    """https://www.pcgamingwiki.com/wiki/Mashed#Jumping_Bug_Fix"""
    util.protontricks('winxp')

    """Hide the launcher"""
    util.append_argument('-VS0 -CS0')
