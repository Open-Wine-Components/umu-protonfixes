""" Game fix for Bejeweled 3
"""
#pylint: disable=C0103 

from protonfixes import util

def main():
    """ game needs d3dcompiler_43 for dx10 mode, but still does not work. disabling dx10 mode allows dx9 mode to work with dxvk
    """
    util.set_environment('PROTON_NO_D3D10', '1')
