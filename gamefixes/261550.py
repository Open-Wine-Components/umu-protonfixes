""" Game fix for Mount & Blade: Bannerlord
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Launcherfix and NVIDIA PhysX support.
    """

    # Fixes the startup process.
    util.replace_command('TaleWorlds.MountAndBlade.Launcher.exe', 'Bannerlord.exe')
    util.set_environment('WINEDLLOVERRIDES','dxgi=n')
    util.set_environment('DXVK_ASYNC','1')

