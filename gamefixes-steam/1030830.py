""" Game fix for Mafia II Definitive Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Enable NVIDIA PhysX support.
    """
    util.protontricks('physx')
