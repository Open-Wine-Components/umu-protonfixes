""" Game fix for Pes 2021
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ 
    """

    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019_ge')
    util.protontricks('allfonts')
    util.protontricks_proton_5('dotnet462')
    util.use_seccomp()
