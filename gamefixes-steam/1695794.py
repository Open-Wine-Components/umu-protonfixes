"""Game fix Halo 3: ODST mod tools"""

from protonfixes import util


def main() -> None:
    # Requires vcrun2019 to launch
    util.protontricks('vcrun2019')
    util.protontricks('d3dcompiler_47')
    util.protontricks('msxml3')
