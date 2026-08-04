"""Game fix for Pantheon: Rise of the Fallen"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    # Standalone launcher fix
    util.protontricks('dotnet48')
    util.protontricks('win10')
