""" Game fix for the Halo Reach mod tools Foundation gamemode. 
Standalone and Sapien seem to work just fine without d3dcompiler_47 and msxml3, although might be required at some deeper level. I just playtested it.
- Oro, @orowith2os
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('dotnet35'))
    util.protontricks('dotnet45')
