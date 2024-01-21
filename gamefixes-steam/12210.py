""" Game fix for GTA IV
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs wmp11
    """
    # Fixes Independence FM user radio station
    util.protontricks('wmp11')
