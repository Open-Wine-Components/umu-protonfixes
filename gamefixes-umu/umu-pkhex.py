"""PKHeX"""

from protonfixes import util


def main() -> None:
    # Needs dotnet, project bumps dotnet version every couple pkhex versions
    util.protontricks('dotnetdesktop9')
