""" Game fix for Star Citizen
"""
#pylint: disable=C0103

import os
from protonfixes import util # pylint: disable=E0401
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

    #override for white/black launcher
    util.winedll_override('libglesv2', 'builtin')
    #override for nvidia cards
    util.winedll_override('nvapi,nvapi64', 'disabled')
    #allow the RSI Launcher to auto-update itself
    util.winedll_override('powershell.exe', 'disabled')

    environments = ["LIVE","PTU","EPTU","TECH-PREVIEW"]

    for env in environments:
        #launcher fails to create these directories in wine so create them here instead
        #https://github.com/starcitizen-lug/knowledge-base/wiki#game-updates
        envPath = os.path.join(util.protonprefix(), "drive_c","Program Files", "Roberts Space Industries", "StarCitizen", env)
        if not os.path.exists(envPath):
            os.makedirs(envPath)
            log("created " + envPath)
