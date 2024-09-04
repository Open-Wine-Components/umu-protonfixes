"""Game fix for Mafia II Definitive Edition"""

from protonfixes import util


def main() -> None:
    """Enable NVIDIA PhysX support."""
    util.protontricks('physx')
