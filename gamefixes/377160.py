""" Game fix for Fallout 4
"""
#pylint: disable=C0103

from protonfixes import util
import subprocess
import os

def main():
    """ Run script extender if it exists.
    """

    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'f4se_loader.exe')):
        util.replace_command('Fallout4Launcher.exe', 'f4se_loader.exe')
