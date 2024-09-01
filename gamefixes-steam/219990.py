"""Game fix for Grim Dawn"""

from protonfixes import util


def main() -> None:
    # Fix black screen. Only needed in a Wine prefix that lacks the DirectX Redist installation that comes with the game installer.
    util.protontricks('d3dcompiler_43')
