"""Ceville
Works with dotnet35sp1 only, now without needing Proton5
Videos still don't work.
"""
import os

from protonfixes import util


def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'


def main() -> None:
    use_xalia = util.protonmain.g_session.env['PROTON_USE_XALIA']
    util.set_environment('PROTON_USE_XALIA', '0')
    util.protontricks('dotnet35sp1')
    util.set_environment('PROTON_USE_XALIA', use_xalia)
