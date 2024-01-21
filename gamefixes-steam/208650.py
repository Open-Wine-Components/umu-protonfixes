""" Game fix for Batman Arkham Knight
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ NVIDIA PhysX support.
    """

    # Enables NVIDIA PhysX in Batman Arkham Knight.
    util.protontricks('physx')
