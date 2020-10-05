""" Game fix for Serious Sam 4
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ This launches the game with the Vulkan renderer by default.
    """

    # Fixes the startup process.
    util.append_argument('util.append_argument('+gfx_strAPI Vulkan')

