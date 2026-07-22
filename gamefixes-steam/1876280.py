"""PAIcom"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    """Crashes unless dotnet48 is installed."""
    util.protontricks('dotnet48')
