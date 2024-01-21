""" Game fix for Chronophantasma Extend
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Uses installs devenum wmp9
    """

    # https://github.com/ValveSoftware/Proton/issues/703#issuecomment-416075961
    util.protontricks('devenum')
    util.protontricks('wmp9_x86_64')
