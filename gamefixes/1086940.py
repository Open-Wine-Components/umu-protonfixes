""" Game fix for Baldur's Gate 3
"""
#pylint: disable=C0103
from protonfixes import util


def main():
    """ Launcher workaround
    """
    # Fixes the startup process.
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')
    util.replace_command('LariLauncher.exe', '../bin/bg3.exe')
