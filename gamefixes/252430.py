""" Game fix for Dusty Revenge: Co-Op Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Install vcrun2010
    """
    util.protontricks('vcrun2010')
    util.protontricks('dsound')
