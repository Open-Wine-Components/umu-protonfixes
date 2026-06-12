"""Ceville
Works with dotnet35sp1 only, now without needing Proton5
Videos still don't work.
"""

from protonfixes import util


def main() -> None:
    util.set_environment('PROTON_NO_XALIA', '1')
    util.protontricks('dotnet35sp1')
    util.set_environment('PROTON_NO_XALIA', '0')
