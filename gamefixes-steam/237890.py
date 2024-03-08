""" Game fix for Agarest: Generations of War
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('wmp9')
    util.winedll_override('winegstreamer', '')
