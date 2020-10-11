""" Game fix for Baldur's Gate 3
"""
#pylint: disable=C0103

from protonfixes import util
from protonfixes import splash
import subprocess


def main():
    """ Launcher workaround
    """
    # Fixes the startup process.
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_47')
    util.replace_command('LariLauncher.exe', '../bin/bg3.exe')
    zenity_bin = splash.sys_zenity_path()
    if not zenity_bin:
        return
    zenity_cmd = ' '.join([zenity_bin, '--question','--text', '"Would you like to run the game with Vulkan? (No = DX11)"', '--no-wrap'])
    zenity = subprocess.Popen(zenity_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    zenity.communicate()
    if zenity.returncode:
        util.replace_command('../bin/bg3.exe', '../bin/bg3_dx11.exe')
        util.set_environment('WINEDLLOVERRIDES','dxgi=n')
