"""Application fix Cxbx-Reloaded emulator"""
#

from protonfixes import util


def main() -> None:
    """Installs vcrun2022, d3dcompiler_47"""
    util.protontricks('vcrun2022')
    util.protontricks('d3dcompiler_47')
