""" Game fix for Gears 5
"""
#pylint: disable=C0103

import glob
import os
import subprocess
from protonfixes import util

def main():
    """ This is a workaround that allows the game to be played with EAC disabled.
    """
    # Fix the startup process:
    if os.path.exists('EasyAntiCheat'):
        if os.path.exists('EasyAntiCheat-backup'):
            subprocess.call(['rm', '-Rf', 'EasyAntiCheat-backup'])
        subprocess.call(['mv', 'EasyAntiCheat', 'EasyAntiCheat-backup'])

    util.replace_command('Gears5_EAC.exe', 'Gears5.exe')

    # Apply proxy dll override:
    # https://github.com/ValveSoftware/Proton/issues/3042#issuecomment-1046904681
    # https://github.com/GloriousEggroll/GFSDK_Aftermath_Lib/
    util.protontricks('GFSDK_Aftermath_Lib')

    tmp = (util.protonprefix() + "drive_c/windows/temp/GFSDK_Aftermath_Lib.x64.dll")
    install_dir = glob.escape(util.get_game_install_path())

    if os.path.exists(install_dir + '/Engine/Binaries/ThirdParty/GFSDK_Aftermath/x64'):
        if not os.path.exists(install_dir + '/Engine/Binaries/ThirdParty/GFSDK_Aftermath/x64-backup'):
            subprocess.call(['mv', install_dir + '/Engine/Binaries/ThirdParty/GFSDK_Aftermath/x64', install_dir + '/Engine/Binaries/ThirdParty/GFSDK_Aftermath/x64-backup'])
            subprocess.call(['mkdir', install_dir + '/Engine/Binaries/ThirdParty/GFSDK_Aftermath/x64'])
        subprocess.call(['cp', tmp, install_dir + '/Engine/Binaries/ThirdParty/GFSDK_Aftermath/x64/'])
