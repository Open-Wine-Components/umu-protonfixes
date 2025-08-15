"""Game fix for Record of Sky: Children of the Light"""

from protonfixes import util


def main() -> None:
    util.set_environment('PROTON_GST_VIDEO_ORIENTATION', 'vertical-flip')
