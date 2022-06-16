""" Game fix for Ys Origin
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs k-lite
    """

    # Fix pre-rendered cutscene playback
    util.protontricks('klite')

