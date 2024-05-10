""" Game fixes Call of Juarez: Gunslinger
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs wmp11
    """
    # Fixes missing cutscenes
    util.protontricks('wmp11')
