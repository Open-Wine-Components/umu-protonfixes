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
    # Fixes the startup process.
    install_dir = glob.escape(util.get_game_install_path())

    for idx, arg in enumerate(sys.argv):
        if '-northstar' in arg:
            if not os.path.isfile(install_dir + '/Titanfall2.exe.bak'):
                subprocess.run(['mv', 'Titanfall2.exe', 'Titanfall2.exe.bak'])
            subprocess.run(['ln', '-s', install_dir + '/NorthstarLauncher.exe', 'Titanfall2.exe'])
        else:
            if os.path.isfile(install_dir + '/Titanfall2.exe.bak'):
                subprocess.run(['mv', 'Titanfall2.exe.bak', 'Titanfall2.exe'])

