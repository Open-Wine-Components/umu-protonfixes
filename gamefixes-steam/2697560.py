"""Game fix for Mojika - Truth Rears Its Ugly Head"""

from protonfixes import util


def main() -> None:
    """Install xact, disable esync, disable fsync"""
    # Fixes the game from crashing or hanging during intro
    util.protontricks('xact')
    util.disable_esync()
    util.disable_fsync()
    # Fixes audio not playing for in-game videos
    util.disable_protonmediaconverter()
