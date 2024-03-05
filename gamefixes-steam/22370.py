""" Game fix for Fallout 3
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    """ Run script extender if it exists.
    """

    if os.path.isfile(os.path.join(os.getcwd(), 'fose_loader.exe')):
        util.replace_command('FalloutLauncher.exe', 'fose_loader.exe')
