"""Game fix for the Halo Reach mod tools Foundation gamemode.
Standalone and Sapien seem to work just fine without d3dcompiler_47 and msxml3, although might be required at some deeper level. I just playtested it.
- Oro, @orowith2os
"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    util.protontricks('dotnet35')
    util.protontricks('dotnet45')
