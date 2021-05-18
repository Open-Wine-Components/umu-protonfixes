""" Installs Origin into game prefix
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019_ge')
    util.protontricks('d3dcompiler_43')
    util.protontricks('d3dcompiler_47')
