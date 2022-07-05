""" Game fix for Darkest Hour: A Hearts of Iron Game
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Set virtual desktop
    """

    # https://github.com/ValveSoftware/Proton/issues/3338
    util.protontricks('vd=1280x720')
