"""Dragon Star Varnir"""

from protonfixes import util


def main():
    """Dragon Star Varnir fix"""
    # Fixes the startup process.
    util.winedll_override('xactengine3_7', 'n')
