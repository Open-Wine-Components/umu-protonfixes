""" Game fix for Age Of Empire 3: Complete Collection
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs corefonts, l3codecx, mfc42, winxp
    """

    # https://github.com/ValveSoftware/Proton/issues/17#issuecomment-415977510
    util.protontricks('mfc42')
    util.protontricks('l3codecx')
    util.protontricks('corefonts')
    util.protontricks('winxp')
