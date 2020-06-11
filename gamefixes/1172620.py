""" Sea of Thieves
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Sea of thieves needs win7
    """

    # https://github.com/ValveSoftware/Proton/issues/200#issuecomment-415905979
    util.protontricks('win7')
