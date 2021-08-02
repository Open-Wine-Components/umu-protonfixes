""" Game fix for Beyond Good and Evil
"""
#pylint: disable=C0103
import os
import urllib.request
from protonfixes import util

def main():
    """ installs dsound d3dx9 arial d3dcompiler_47
    """

    util.protontricks('dsound')
    util.protontricks('d3dx9')
    util.protontricks('arial')
    util.protontricks('d3dcompiler_47')

    installpath = os.path.abspath(os.getcwd())
    url = "https://github.com/legluondunet/MyLittleLutrisScripts/raw/master/Beyond%20Good%20and%20Evil/dsound.dll"

    """ Download dsound.dll in the game folder
    """

    if not os.path.isfile(os.path.join(installpath, 'dsound.dll')):
        urllib.request.urlretrieve (url, "dsound.dll")

    """ Add a couple of keys in regedit
    """

    util.regedit_add("HKLM\\Software\\Wow6432Node\\Ubisoft")
    util.regedit_add("HKLM\\Software\\Wow6432Node\\Ubisoft\\Beyond Good & Evil",'InstallLanguage','REG_DWORD','1')
