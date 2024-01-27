""" Madden NFL 21 needs vcrun2019 for online mode to work
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019_ge')

