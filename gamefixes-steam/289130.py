"""Game fix for Endless Legend"""

from protonfixes import util


def main():
    """Enable -useembedded to get past loading hang"""
    # Enable preload options
    util.append_argument('-useembedded')
