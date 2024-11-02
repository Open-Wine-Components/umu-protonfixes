"""Game fix for Silent Hill 3"""

from protonfixes import util


def main() -> None:

    # Set SteamGameId so that non-steam versions can pick up steam-specific fixes in proton's wine code
    util.set_environment('SteamGameId', 'silenthill3')
