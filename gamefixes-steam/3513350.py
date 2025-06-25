"""Wuthering Waves - ID 3513350
https://www.protondb.com/app/3513350
"""

from protonfixes import util


def main() -> None:
    """In-game browser fix."""
    util.wineexe_override('KRSDKExternal', util.OverrideOrder.DISABLED)
    """Font fixes for in-game resources, if any."""
    util.protontricks('sourcehansans')
    util.protontricks('fakechinese')
    util.protontricks('corefonts')
