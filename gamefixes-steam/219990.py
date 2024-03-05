""" Game fix for Grim Dawn
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    """ Run script extender if it exists.
    """

    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'GrimInternals64.exe')):
        util.replace_command('Grim Dawn.exe', 'GrimInternals64.exe')

    # Fixes a black screen being rendered:
    util.protontricks('d3dcompiler_43')
