""" Memento Mori
wmp11 (Fixes missing logo videos and problems with working videos)
hangs on logo without override
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('libvkd3d-1', 'n')
    util.protontricks('wmp11')
