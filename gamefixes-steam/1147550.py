"""Game fix for Not For Broadcast"""

from protonfixes import util


def main() -> None:
    # Force using winegstreamer instead of winedmo for video playback
    # Fixes video/game freezing and crashing
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
