"""Persona 3 Reload"""

from protonfixes import util


def main() -> None:
    """Imports demo saves into the full game."""
    util.import_saves_folder(
        3358440, f'AppData/Roaming/SEGA/P3R/Steam/{util.get_steam_account_id()}', True
    )
