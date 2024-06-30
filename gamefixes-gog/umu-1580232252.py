""" Resident Evil (1997)
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('ddraw', 'n,b')
    util.winedll_override('dinput', 'n,b')
