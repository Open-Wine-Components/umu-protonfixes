""" GWENT: The Witcher Card Game
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs mfc140

    mfc140 is necessary to start the game up. GOG login happens inside the Steam overlay.

    vcrun2019_ge enables full support of the prelauncher interface. GOG login inside the prelauncher.
    This prelauncher is not necessary for the Game. If only mfc is present, it's skipped.
    """

    util.protontricks('mfc140')
