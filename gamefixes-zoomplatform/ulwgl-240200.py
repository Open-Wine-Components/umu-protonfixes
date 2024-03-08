""" Duke Nukem: Manhattan Project - Enhanced Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.winedll_override('d3d8', 'n,b')
    util.protontricks('vcrun2019')
