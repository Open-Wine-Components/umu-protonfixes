"""Helldivers 2"""

from protonfixes import util


def main() -> None:
    """Installs prevent cursor from leaving window in borderless mode"""
    util.protontricks('grabfullscreen=y')
