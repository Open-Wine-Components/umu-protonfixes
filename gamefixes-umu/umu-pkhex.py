"""PKHeX"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    # Needs dotnet, project bumps dotnet version every couple pkhex versions
    util.protontricks('dotnetdesktop9')
