"""
The Wheel of Time
"""

from protonfixes import util


def main():
    util.winedll_override('ddraw', 'n,b')  # GOG's dxcfg
