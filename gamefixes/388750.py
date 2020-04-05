""" Game fix for Chronophantasma Extend
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Uses win32 prefix, installs devenum wmp9
    """

    # Winetrick wmp9 requires 32bit prefix
    util.use_win32_prefix()

    # https://github.com/ValveSoftware/Proton/issues/703#issuecomment-416075961
    util.protontricks('devenum')
    util.protontricks('wmp9')
