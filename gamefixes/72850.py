""" Game fix for Skyrim
"""
#pylint: disable=C0103

from protonfixes import util
import subprocess
import os

def main():
    """ Run script extender if it exists.
    """

    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'skse_loader.exe')):
        util.replace_command('SkyrimLauncher.exe', 'skse_loader.exe')

