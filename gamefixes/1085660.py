""" Game fix for Destiny 2
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs vcrun2019
    """

    util.protontricks('vcrun2019_ge')
    util.set_environment('DXVK_LOG_PATH','none')
