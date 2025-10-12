"""Forza Horizon 4"""

from protonfixes import util


def main() -> None:
    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019')
