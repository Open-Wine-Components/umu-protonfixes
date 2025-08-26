"""ARK: Survival Evolved"""

from protonfixes import util


def main() -> None:
    """Video Playback Fix"""
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
