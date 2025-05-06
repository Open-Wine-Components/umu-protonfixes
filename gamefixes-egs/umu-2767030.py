"""Game fix for Marvel Rivals"""
# EGS-ID 575efd0b5dd54429b035ffc8fe2d36d0

from protonfixes import util


def main() -> None:

    util.replace_command('epic_launch_helper.exe', 'MarvelRivals_Launcher.exe')

    # Set SteamGameId so that non-steam versions can pick up steam-specific fixes in proton's wine code
    util.set_environment('SteamGameId', '2767030')
    
    # Set SteamDeck=1 to be able to launch the game
    util.set_environment('SteamDeck', '1')

