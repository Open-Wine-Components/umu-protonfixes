"""Application fix Artificial Academy 2
Launcher game settings: Disable wine3d, enable win10fix
"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    """Installs fakejapanese_ipamona vcrun2015 dotnetcore3"""
    util.protontricks('vcrun2015')
    util.protontricks('dotnetcore3')
    util.protontricks('fakejapanese_ipamona')
