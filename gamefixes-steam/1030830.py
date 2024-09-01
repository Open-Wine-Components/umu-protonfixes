"""Game fix for Mafia II Definitive Edition"""

from protonfixes import util


def main():
    """Enable NVIDIA PhysX support."""
    util.protontricks('physx')
