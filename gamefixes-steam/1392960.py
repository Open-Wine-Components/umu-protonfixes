"""Game fix for STORY OF SEASONS: Pioneers of Olive Town"""

from protonfixes import util


def main() -> None:
    # Wont boot without them, sadly doesn't fix DLC not actually loading in game, casefolding issue?
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
