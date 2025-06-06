"""Deltarune"""

from protonfixes import util


def main() -> None:
    """Imports demo saves into the full game."""
    util.import_saves_folder(1690940, 'AppData/Local/DELTARUNE', True)
