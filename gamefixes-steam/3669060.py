"""Game fix for Blade & Soul NEO"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    util.protontricks('hidewineexports=enable')
    util.protontricks('dotnet48')
