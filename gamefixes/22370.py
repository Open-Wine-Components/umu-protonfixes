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

    # Fixes the startup process.
    if not os.path.isfile(os.path.join(os.getcwd(), 'xlive.dll')):
        xlivepath = os.path.join(util.protonprefix(), 'drive_c/windows/syswow64/xlive.dll')
        shutil.copy(xlivepath, os.path.join(os.getcwd(), 'xlive.dll'))
    if os.path.isfile(os.path.join(os.getcwd(), 'fose_loader.exe')):
        util.replace_command('FalloutLauncher.exe', 'fose_loader.exe')
