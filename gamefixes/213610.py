""" Sonic Adventure 2
"""
#pylint: disable=C0103

import os
import shutil
import subprocess
from protonfixes import util

def main():
    """ Fix the hyper speed issue when the framerate is over 60.
    """

    util.set_environment('DXVK_FRAME_RATE', '60')
