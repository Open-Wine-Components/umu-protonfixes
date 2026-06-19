"""Tex Murphy: Overseer.

Use packaged D7VK for the game's DirectDraw / Direct3D 7 renderer.
"""

from protonfixes import util


def main() -> None:
    util.set_environment('PROTON_USE_D7VK', '1')
