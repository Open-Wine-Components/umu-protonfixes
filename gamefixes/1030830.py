""" Game fix for Mafia II Definitive Edition
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Launcherfix and NVIDIA PhysX support.
    """

    # Fixes the startup process.
    util.replace_command('Launcher.exe', '../Mafia II Definitive Edition.exe')
