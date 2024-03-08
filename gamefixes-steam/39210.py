""" Game fix for FFXIV
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():
    """ FFXIV add NOSTEAM option.
    """
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('-issteam', '')
