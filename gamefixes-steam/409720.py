"""Game fix for BioShock 2 Remastered"""

from protonfixes import util


def main() -> None:
    """Disable ESYNC, disable intro's"""

    # After loading the game, or a save file, a key needs to be pressed
    # to continue. That screen does not respond to keyboard or mouse,
    # so there is no way to continue. -nointro disables that screen
    # (but also the intro's at the start of the game).
    util.append_argument('-nointro')

    # ESYNC causes texture problems and frequent hangs.
    util.disable_esync()
