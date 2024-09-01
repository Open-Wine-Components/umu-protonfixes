"""Game fix for Agarest: Generations of War"""

from protonfixes import util


def main():
    util.protontricks('wmp9')
    util.winedll_override('winegstreamer', '')
