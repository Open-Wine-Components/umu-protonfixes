"""The Testament of Sherlock Holmes"""

from protonfixes import util


def main() -> None:
    """Needs to have PhysX installed to work, even for systems not using Nvidia."""
    util.protontricks('physx')
