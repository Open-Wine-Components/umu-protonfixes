""" Game fix for Mount & Blade: Bannerlord
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util

def main():
    """ Launcherfix and NVIDIA PhysX support.
    """

    # Fixes the startup process.
    util.set_environment('WINEDLLOVERRIDES','dxgi=n')
    util.set_environment('DXVK_ASYNC','1')

    installpath = os.getcwd()

    if not os.path.isfile(os.path.join(os.path.abspath(installpath), 'bin', 'Win64_Shipping_Client', 'ManagedStarter.exe')):
        subprocess.call(['ln', '-s', 'Bannerlord.exe', 'ManagedStarter.exe'])

    if not os.path.isfile(os.path.join(os.path.abspath(installpath),  'bin', 'Win64_Shipping_Client', 'ManagedStarter_BE.exe')):
        subprocess.call(['ln', '-s', 'Bannerlord_BE.exe', 'ManagedStarter_BE.exe'])
