"""God of War Ragnarök"""

from protonfixes import util


def main() -> None:
    """Game needs SteamDeck=1 to avoid PlayStation SDK install error."""
    util.set_environment('SteamDeck', '1')

