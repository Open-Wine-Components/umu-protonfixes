""" Game fix for Guild Wars 2
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ GW2 add NOSTEAM option.
    """
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('-provider', '')
