"""Game fix for Transformers: War for Cybertron"""

from protonfixes import util


def main() -> None:
    """Installs physx library, without it the game simply won't launch"""
    util.protontricks('physx')
