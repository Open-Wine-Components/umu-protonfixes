"""Epic Mickey 2"""

from protonfixes import util


def main() -> None:
    """Green textures depending on where the game is installed."""
    util.set_game_drive(True)
