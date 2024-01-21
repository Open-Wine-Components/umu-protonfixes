""" Game fix for Ys Origin
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs k-lite
    """

    util.protontricks('vcrun2008')
    util.protontricks('quartz')
    util.protontricks('amstream')
    util.protontricks('xvid')
    util.protontricks('win7')
    util.disable_protonaudioconverter()
