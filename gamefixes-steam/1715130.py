"""Crysis Remastered"""

from protonfixes import util


def main() -> None:
    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2022')
    util.protontricks('d3dcompiler_43')
