"""Game fix for The Legend of Heroes: Trails in the Sky SC"""

from .. import util


def main() -> None:
    util.protontricks('quartz')  # Cutscene fixes
    util.protontricks('amstream')
    util.protontricks('lavfilters')
    util.winedll_override('dinput8', util.DllOverride.NATIVE_BUILTIN)  # Set for the SoraVoice mod
