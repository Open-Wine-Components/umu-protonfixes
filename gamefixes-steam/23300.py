"""Yosumin"""

from protonfixes import util


def main() -> None:
    """Works around a Wine bug causing the game to crash."""
    util.protontricks('d3dx9')
