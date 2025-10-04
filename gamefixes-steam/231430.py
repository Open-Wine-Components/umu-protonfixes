"""Company Of Heroes 2"""

from protonfixes import util


def main() -> None:
    # Needed to fix multiplayer desync
    util.protontricks('ucrtbase2019')
