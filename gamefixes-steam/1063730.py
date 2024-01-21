""" Game fix for New World
"""
#pylint: disable=C0103

import glob
import os
import subprocess
from protonfixes import util

def main():
    """ Launcher currently broken
    """
    # Fix the startup process:
    util.replace_command('NewWorldLauncher.exe', 'Bin64/NewWorld.exe')
