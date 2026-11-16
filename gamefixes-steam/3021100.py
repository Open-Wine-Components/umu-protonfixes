"""Game fix for Five Hearts Under One Roof"""

from protonfixes import util


def main() -> None:
    """Installs lavfilters to resolve black screen / missing video playback in FMV cutscenes."""
    util.protontricks('lavfilters')
