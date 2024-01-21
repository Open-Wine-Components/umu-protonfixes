""" Game fix for Mortal Kombat X
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """
    """

    # Fix pre-rendered cutscene playback
    util.protontricks('xact_x64')

