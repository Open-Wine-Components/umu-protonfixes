""" Game fix for Total War: Rome II
"""

from protonfixes import util

def main():
    """ installs d3dx11_42, d3dcompiler_42, directplay
        Disable esync and fsync
    """

    util.protontricks('d3dx11_42')
    util.protontricks('d3dcompiler_42')
    util.protontricks('directplay')
    
    util.disable_esync()
    util.disable_fsync()
