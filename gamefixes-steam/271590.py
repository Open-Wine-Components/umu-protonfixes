"""Game fix for GTAV"""

from protonfixes import util


def main() -> None:
    """Game fix for GTAV"""
    # Set SteamGameId so that non-steam versions can pick up steam-specific fixes in proton's wine code
    util.set_environment('SteamGameId', '271590')
