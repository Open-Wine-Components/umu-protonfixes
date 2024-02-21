""" Hardwar
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('dinput', 'n,b') # DxWrapper component
    util.winedll_override('winmm', 'n,b') # Music playback
