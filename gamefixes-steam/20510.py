""" Game fix for S.T.A.L.K.E.R.: Clear Sky
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dcomp43, d3dcomp46, d3dcomp47, directplay
    """

    # from Discord report in #proton-gaming by @thebigboo_ 
    # fix crashing from d3d comp errors
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_46')
    util.protontricks('d3dcompiler_47')
    # fixes multiplayer
    util.protontricks('directplay')
