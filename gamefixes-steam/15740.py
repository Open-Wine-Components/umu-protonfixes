""" Game fix for Oddworld: Munch's Oddysee
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs devenum, quartz, wmp9
    """

    # https://appdb.winehq.org/objectManager.php?sClass=version&iId=34367
    util.protontricks('devenum')
    util.protontricks('quartz')
    util.protontricks('wmp9_x86_64')
