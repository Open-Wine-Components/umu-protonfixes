""" Game fix for Grim Dawn
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    # Run script extender if it exists:
    if os.path.isfile(os.path.join(os.getcwd(), 'GrimInternals64.exe')):
        util.replace_command('Grim Dawn.exe', 'GrimInternals64.exe')

    # Fix black screen. Needed for the expansions, not for the base game:
    util.protontricks('d3dcompiler_43')
