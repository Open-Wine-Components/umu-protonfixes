""" Game fix for Titanfall 2
"""
#pylint: disable=C0103

from protonfixes import util
import os
import sys
import subprocess
import glob

def main():
    """ Allow -northstar option to work
    """
    # Define game directory
    install_dir = glob.escape(util.get_game_install_path())

    # Restore original titanfall2.exe if NorthstarLauncher.exe was previously symlinked
    if os.path.isfile(install_dir + '/Titanfall2.exe.bak'):
        subprocess.run(['mv', 'Titanfall2.exe.bak', 'Titanfall2.exe'])
