""" Oddworld: Stranger's Wrath HD
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('mfc90') # The game crashes on launch without mfc90
