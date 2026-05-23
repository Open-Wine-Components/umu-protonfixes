"""Game fix for Chronology"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    """Add dotnet"""
    util.protontricks('dotnet20')
    util.protontricks('dotnet40')
