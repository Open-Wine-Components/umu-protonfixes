""" Game fix for Conan Exiles
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ Launcher workaround
    """
    # Fixes the startup process.
    util.install_battleye_runtime()
    util.replace_command('FuncomLauncher.exe', '../ConanSandbox/Binaries/Win64/ConanSandbox.exe')
    util.append_argument('-BattlEye')

