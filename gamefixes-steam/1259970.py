"""Game fix for Pes 2021"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    # Replace launcher with game exe in proton arguments
    util.protontricks('vcrun2019')
    util.protontricks('allfonts')
    util.protontricks('dotnet462')
