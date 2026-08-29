"""Game fix for Way of the Samurai 4"""

from protonfixes import util


def main() -> None:
    """Fix DirectShow .wmv video playback crash."""
    util.protontricks('directshow')
    util.protontricks('lavfilters')
