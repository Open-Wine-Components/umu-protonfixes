""" Game fix for Skyrim
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    """ Run script extender if it exists.
    """

    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'skse_loader.exe')):
        if 'MODS' in os.environ:
            util.replace_command('SkyrimLauncher.exe', 'skse_loader.exe')
