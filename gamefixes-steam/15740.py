""" Game fix for Oddworld: Munch's Oddysee
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ klite to fix videos
        prev version of this used devenum, quartz, wmp9 but that caused laggy intros
    """
    util.protontricks('klite')
