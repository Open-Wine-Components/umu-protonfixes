""" Game fix for Fallout 76
"""
#pylint: disable=C0103
from protonfixes import util

def main():
    """ Ensure Faudio is installed so UI and NPC audio and music is audible
    """
    util.protontricks('faudio')
