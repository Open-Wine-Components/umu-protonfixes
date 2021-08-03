""" Game fix for ArcaniA
"""
#pylint: disable=C0103
from protonfixes import util

def main():
    """ installs xact_x64 wmp11 physx
    """

    util.protontricks('xact_x64')
    util.protontricks('wmp11')
    util.protontricks('physx')