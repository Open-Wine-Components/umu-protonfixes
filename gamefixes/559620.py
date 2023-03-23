""" Game fix for Outlaws + A Handful of Missions
"""
#pylint: disable=C0103
#
from protonfixes import util

def main():
    # Fix the (awesome) cutscenes.
    util.protontricks('cnc_ddraw')

    # Game ships with a WinMM replacement for CD music.
    util.winedll_override('winmm', 'n,b')
