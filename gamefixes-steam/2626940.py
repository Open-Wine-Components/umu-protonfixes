"""Life Makeover - ID 2626940
https://www.protondb.com/app/2626940
"""

from protonfixes import util


def main() -> None:
    """Video Playback Fix"""
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
