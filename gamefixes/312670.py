""" Game fix for Borderlands 2
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Launcherfix and NVIDIA PhysX support.
    """

    # Fixes the startup process.
    util.replace_command('StrangeBrigade.exe', 'StrangeBrigade_Vulkan.exe')
    util.append_argument('-skipdrivercheck -noHDR')

