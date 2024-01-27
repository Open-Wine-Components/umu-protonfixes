""" Game fix for FFXIV
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ FFXIV add NOSTEAM option.
    """
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('-issteam', '')
