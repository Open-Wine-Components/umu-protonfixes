""" Game fix for Black Desert Online
"""
#pylint: disable=C0103

from protonfixes import util
import os

def main():
    """ Black Desert Online add NOSTEAM option.
    """
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('--steam', '')
