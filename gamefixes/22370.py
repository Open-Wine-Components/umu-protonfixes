""" Game fix for Fallout 3
"""
#pylint: disable=C0103

from protonfixes import util
import subprocess
import os
import shutil

def main():
    """ Run script extender if it exists.
    """

    if os.path.isfile(os.path.join(os.getcwd(), 'fose_loader.exe')):
        util.replace_command('FalloutLauncher.exe', 'fose_loader.exe')
