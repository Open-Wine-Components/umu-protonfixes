"""Game fix for Resident Evil 7"""

from protonfixes import util


def main() -> None:
    # Force using winegstreamer instead of winedmo for video playback
    util.set_environment('PROTON_MEDIA_USE_GST', '1')
