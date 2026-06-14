"""Game fix for Project Torque"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    """Game needs dotnet35 to launch"""
    """https://bugs.winehq.org/show_bug.cgi?id=57666"""
    util.protontricks('dotnet35sp1')
    util.protontricks('win10')
