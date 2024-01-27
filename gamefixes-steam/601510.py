""" Yu-Gi-Oh Duel Links needs vcrun2019
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019_ge')
