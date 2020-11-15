""" Game fix for Serious Sam 4
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util

def main():
    """ Graphics API workaround
    """
    util.protontricks('d3dcompiler_47')
    if not os.path.isfile('UserCfg.lua.bak'):
        subprocess.call(['cp', 'UserCfg.lua', 'UserCfg.lua.bak'])
        f = open('UserCfg.lua',"a+")
        f.write("gfx_strAPI = \"Vulkan\";\nsfx_strAPI = \"OpenAL\";\nren_bDepthPrepass = 0;")
        f.close

    if not os.path.isfile('Content/SeriousSam4/Config/Content/SeriousSam4/Config/CheckDriver.lua.bak'):
        subprocess.call(['cp', 'Content/SeriousSam4/Config/CheckDriver.lua', 'Content/SeriousSam4/Config/CheckDriver.lua.bak'])
        f = open('Content/SeriousSam4/Config/CheckDriver.lua',"rt")
        data = f.read()
        data = data.replace('gfx_iReqDriverVersion = 1100;', 'gfx_iReqDriverVersion = 1000;')
        f.close()
        f = open('Content/SeriousSam4/Config/CheckDriver.lua',"wt")
        f.write(data)
        f.close()

