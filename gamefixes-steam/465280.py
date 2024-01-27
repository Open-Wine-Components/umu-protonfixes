""" Game fix for Yesterday Origins
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Set to win7
    """

    # Fixes black screen during cutscenes.
    util.protontricks('win7')
