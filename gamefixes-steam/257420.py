""" Game fix for Serious Sam 4
"""
#pylint: disable=C0103

import os
import subprocess
from protonfixes import util

def main():
    """ Graphics API workaround
    """
    if not os.path.isfile('UserCfg.lua.bak'):
        subprocess.call(['cp', 'UserCfg.lua', 'UserCfg.lua.bak'])
        f = open('UserCfg.lua',"a+")
        f.write("sfx_strAPI = \"OpenAL\";")
        f.close
