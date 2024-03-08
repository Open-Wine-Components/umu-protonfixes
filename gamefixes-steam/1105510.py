""" Game fix for Yakuza 5
"""
#pylint: disable=C0103
from protonfixes import util

def main():
    """ Needs WINE_DISABLE_SFN set from this patch: https://github.com/ValveSoftware/wine/pull/205
    """
    util.set_environment('WINE_DISABLE_SFN', '1')
