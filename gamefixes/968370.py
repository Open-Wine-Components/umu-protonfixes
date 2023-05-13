""" The Blind Prophet
garbled fonts & No cursive font (Segoe Script)
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.set_environment('WINEDLLOVERRIDES', 'd3d9=d')
    #util.append_argument('/NOF')
    #util.set_environment('PROTON_USE_WINED3D9', '1')
    #util.disable_dxvk()
    util.protontricks('segoe_script5')
