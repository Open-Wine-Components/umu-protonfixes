r"""Fix for S\&box Editor"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    r"""Installs  dotnetdesktop10 for the S\&box editor"""
    util.protontricks('dotnetdesktop10')
