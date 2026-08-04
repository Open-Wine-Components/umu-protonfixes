"""Assassin's Creed: Black Flag Resynced"""

from protonfixes import util


def main() -> None:
    """Works around a regression in Proton 11, which is causing the game to crash unless NTSync is disabled."""
    util.disable_ntsync()
