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
        f.write("gfx_strAPI = \"Direct3D12\";\nsfx_strAPI = \"OpenAL\";")
        f.close

    if not os.path.isfile('Content/SeriousSam4/Config/CheckDriver.lua.bak'):
        subprocess.call(['cp', 'Content/SeriousSam4/Config/CheckDriver.lua', 'Content/SeriousSam4/Config/CheckDriver.lua.bak'])
        pattern = "gfx_iReqDriverVersion ="
        file = open(r'Content/SeriousSam4/Config/CheckDriver.lua','r')
        result = open(r'Content/SeriousSam4/Config/CheckDriver2.lua', 'w')  
        for line in file:
            line = line.strip('\r\n')  # it's always a good behave to strip what you read from files
            if pattern in line:
                line = "gfx_strAPI = \"Vulkan\";"  # if match, replace line
            result.write(line + '\n')  # write every line
        file.close()  # don't forget to close file handle
        result.close()
        subprocess.call(['mv', 'Content/SeriousSam4/Config/CheckDriver2.lua', 'Content/SeriousSam4/Config/CheckDriver.lua'])

