""" Hyperdimension Neptunia Re;Birth2
Poor performance on some AMD hardware
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.set_environment('radeonsi_disable_sam', 'true')
    util.set_environment('AMD_DEBUG', 'nowc')
