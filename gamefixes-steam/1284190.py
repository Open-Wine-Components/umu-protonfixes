"""Planet Crafter"""

from protonfixes import util


def main() -> None:
    """Imports demo saves into the full game."""
    util.import_saves_folder(1754850, 'AppData/LocalLow/MijuGames/Planet Crafter', True)
