"""Metaphor ReFantazio"""

from protonfixes import util


def main() -> None:
    """Imports demo saves into the full game."""
    util.import_saves_folder(
        3130330,
        f'AppData/Roaming/SEGA/METAPHOR/Steam/{util.get_steam_account_id()}',
        True,
    )
