""" Game fix for Conan Exiles
"""
#pylint: disable=C0103
from protonfixes import util


def main():
    """ Launcher workaround
    """
    # Fixes the startup process.
    util.replace_command('FuncomLauncher.exe', '../ConanSandbox/Binaries/Win64/ConanSandbox.exe')
