"""Setup for all EGS games (EGL will do this normally)"""

from protonfixes import util


def main() -> None:
    util.protontricks('vcrun2022')
    util.regedit_add('HKCR\\com.epicgames.launcher')
