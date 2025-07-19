"""Game fix Summoner's War Chronicles"""

from protonfixes import util


def main() -> None:
    # Setting SteamDeck=0 restores the original login method, allowing users to bypass forced account linking and log in as intended.
    util.set_environment('SteamDeck', '0')
