""" Game fix for Grim Dawn
"""
#pylint: disable=C0103

from protonfixes import util
from protonfixes import splash
import subprocess
import os

def main():
    """ Run script extender if it exists.
    """

    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'GrimInternals64.exe')):
        zenity_bin = splash.sys_zenity_path()
        if not zenity_bin:
            return
        zenity_cmd = ' '.join([zenity_bin, '--question','--text', '"Would you like to run the game with Grim Internals?"', '--no-wrap'])
        zenity = subprocess.Popen(zenity_cmd, shell=True)
        zenity.communicate()
        if not zenity.returncode:
            util.replace_command('Grim Dawn.exe', 'GrimInternals64.exe')
