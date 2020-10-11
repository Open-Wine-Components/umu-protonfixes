""" Game fix for Serious Sam 4
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util
from protonfixes import splash

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

    zenity_bin = splash.sys_zenity_path()
    if not zenity_bin:
        return
    zenity_cmd = ' '.join([zenity_bin, '--question','--text', '"Would you like to run the game with Vulkan? (No = DX11)"', '--no-wrap'])
    zenity = subprocess.Popen(zenity_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    zenity.communicate()
    if zenity.returncode:
        util.set_environment('WINEDLLOVERRIDES','dxgi=n')
        f = open("UserCfg.lua", "r")
        for line in f:
            if "Vulkan" in line:
                f = open('UserCfg.lua',"rt")
                data = f.read()
                data = data.replace('gfx_strAPI = "Vulkan";', 'gfx_strAPI = "Direct3D11";')
                f.close()
                f = open('UserCfg.lua',"wt")
                f.write(data)
                f.close()
            if "Direct3D12" in line:
                f = open('UserCfg.lua',"rt")
                data = f.read()
                data = data.replace('gfx_strAPI = "Direct3D12";', 'gfx_strAPI = "Direct3D11";')
                f.close()
                f = open('UserCfg.lua',"wt")
                f.write(data)
                f.close()
    else:
        f = open("UserCfg.lua", "r")
        for line in f:
            if "Direct3D11" in line:
                f = open('UserCfg.lua',"rt")
                data = f.read()
                data = data.replace('gfx_strAPI = "Direct3D11";', 'gfx_strAPI = "Vulkan";')
                f.close()
                f = open('UserCfg.lua',"wt")
                f.write(data)
                f.close()
            if "Direct3D12" in line:
                f = open('UserCfg.lua',"rt")
                data = f.read()
                data = data.replace('gfx_strAPI = "Direct3D12";', 'gfx_strAPI = "Vulkan";')
                f.close()
                f = open('UserCfg.lua',"wt")
                f.write(data)
                f.close()
