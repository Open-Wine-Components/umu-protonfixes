""" Game fix for Sonic CD
"""
#pylint: disable=C0103 

from protonfixes import util

def main():
    """ Installs d3dcompiler_43, d3dx9_43, mdx. Locks fps to 60.
    """

    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dx9_43')
    util.protontricks('mdx')

    util.set_environment('DXVK_FRAME_RATE', '60')
