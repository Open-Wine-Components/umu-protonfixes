"""Ougon Musoukyoku"""

from protonfixes import util


def main() -> None:
    # Codecs required for opening playback
    util.protontricks('lavfilters')
