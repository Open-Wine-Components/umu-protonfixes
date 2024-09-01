"""Game fix for Batman Arkham Knight"""

from protonfixes import util


def main():
    """NVIDIA PhysX support."""

    # Enables NVIDIA PhysX in Batman Arkham Knight.
    util.protontricks('physx')
