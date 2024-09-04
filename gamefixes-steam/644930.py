"""They Are Billions"""

from protonfixes import util


def main() -> None:
    # fix broken or missing font in UI
    util.protontricks('gdiplus')
