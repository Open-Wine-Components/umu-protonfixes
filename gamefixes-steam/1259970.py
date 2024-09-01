"""Game fix for Pes 2021"""

from protonfixes import util


def main():
    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019')
    util.protontricks('allfonts')
    util.protontricks('dotnet462')
