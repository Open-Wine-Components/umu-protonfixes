""" Game fix for Oceanhorn: Monster of Uncharted Seas
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs d3dx10_43, d3dcompiler_43, d3dcompiler_47
    """

    # https://github.com/ValveSoftware/Proton/issues/2556#issuecomment-983185082
    util.protontricks('d3dx10_43')
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
