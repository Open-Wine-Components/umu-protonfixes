"""Game fix for Akiba's Trip: Undead & Undressed"""

from protonfixes import util


def main() -> None:
    util.set_environment('PROTON_GST_VIDEO_ORIENTATION', 'vertical-flip')
