""" Game fix for Skyrim SE
"""
#pylint: disable=C0103

from protonfixes import util
import subprocess
import os

def main():
    """ Run script extender if it exists.
    """

    if os.path.isfile(os.path.join(os.getcwd(), 'skse64_loader.exe')):
        util.replace_command('SkyrimSELauncher.exe', 'skse64_loader.exe')
