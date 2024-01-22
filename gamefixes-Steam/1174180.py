""" Game fix for Red Dead Redemption 2
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    """ Sometimes game will not launch if -fullscreen -vulkan is not specified
    """

    util.append_argument('-fullscreen -vulkan')
