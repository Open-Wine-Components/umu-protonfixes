"""Wuthering Waves - ID 3513350
https://www.protondb.com/app/3513350
"""

from protonfixes import util


def main() -> None:
    """Font fixes for in-game resources, if any."""
    util.protontricks('sourcehansans')
    util.protontricks('fakechinese')
    util.protontricks('corefonts')

    """As of version 3.4, SteamOS/SteamDeck env vars force a broken plugin in-game to play videos."""
    """Unsetting them to also prevent issues on Steam Decks where they are set by default."""
    util.del_environment('SteamOS')
    util.del_environment('SteamDeck')
