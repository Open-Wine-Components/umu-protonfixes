"""The Last of Us Part 2 Remastered"""

from protonfixes import util


def main() -> None:
    """Fixes the game not starting for some people, but it doesn't work for everyone though. Cause has yet to be determined."""
    util.set_environment('SteamDeck', '1')
