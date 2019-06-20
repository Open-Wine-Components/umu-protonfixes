""" Game fix for Fallout New Vegas
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ Run script extender if it exists.
    """

    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'nvse_loader.exe')):
        util.replace_command('FalloutNVLauncher.exe', 'nvse_loader.exe')
