"""Octopath Traveler 2"""

from protonfixes import util


def main() -> None:
    """Imports demo saves into the full game's prefix"""
    util.import_saves_folder(
        2203230,
        f'Documents/My Games/Octopath_Traveler2/Steam/{util.get_steam_account_id()}/SaveGames',
        True,
    )
