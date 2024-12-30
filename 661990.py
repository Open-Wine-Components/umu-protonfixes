"""Arcana Heart 3"""

from protonfixes import util


def main() -> None:
    """Plays at wrong speed at frame rates higher than 60 FPS."""
    util.set_environment('DXVK_FRAME_RATE', '60')