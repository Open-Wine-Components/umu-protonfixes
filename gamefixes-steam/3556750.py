"""Warhammer 40,000: Dawn of War - Definitive Edition"""

from protonfixes import util


def main() -> None:
    # Needed to fix multiplayer desync
    util.protontricks('ucrtbase2019')
