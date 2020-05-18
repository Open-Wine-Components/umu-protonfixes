""" Game fix for Styx: Master of Shadows
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Install dotnet40
    """

    # https://github.com/ValveSoftware/Proton/issues/810
    # https://steamcommunity.com/app/242640/discussions/0/620700960990638817/
    util.protontricks('dotnet40')
    util.protontricks('nocrashdialog')