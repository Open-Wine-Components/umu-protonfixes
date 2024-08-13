""" Game fix for Star Citizen
"""
#pylint: disable=C0103,E0401

import os
from protonfixes import util
from protonfixes.logger import log

def main():
    """ EAC Workaround
    """

    #eac workaround
    util.set_environment('EOS_USE_ANTICHEATCLIENTNULL','1')

    #needed for nvidia vulkan
    util.set_environment('WINE_HIDE_NVIDIA_GPU','1')

    #needed for amd vulkan
    util.set_environment('dual_color_blend_by_location','true')

    #allow the RSI Launcher to auto-update itself
    util.protontricks('powershell')
