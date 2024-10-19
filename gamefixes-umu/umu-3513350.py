"""Wuthering Waves - ID 3513350
https://www.protondb.com/app/3513350
"""

from protonfixes import util


def main() -> None:
    """Video playback glitches in 2.1+ content
    This disables Proton mfplat at the cost
    of in-game experience for now.
    """
    util.winedll_override('mfplat', util.OverrideOrder.DISABLED)
    """In-game browser fix."""
    util.wineexe_override('KRSDKExternal', util.OverrideOrder.DISABLED)
    """Font fixes for in-game resources, if any."""
    util.protontricks('sourcehansans')
    util.protontricks('fakechinese')
    util.protontricks('corefonts')
    """Set SteamGameId so that non-steam versions can
    pick up steam-specific fixes in proton's wine code
    if, when and should such fixes ever land.
    """
    util.set_environment('SteamGameId', '3513350')
