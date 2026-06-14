"""Zeit²"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    """Needs dotnet48 installed to avoid crashing."""
    util.protontricks('dotnet48')
