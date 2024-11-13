"""Game fix for Dirt 3 Complete Edition"""


from protonfixes import util


def main() -> None:
    """Installs OpenAL library, without it the game simply wont launch on newer proton version's"""
    util.protontricks('Openal')
