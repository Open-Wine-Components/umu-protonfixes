"""Game fix for MapleStory"""

from protonfixes import util


def main() -> None:
    """Report Windows 10 to the client, Nexon Steam connector, and helper.

    The launcher/anti-cheat handoff expects a supported OS version.
    """
    for exe in ('MapleStory.exe', 'nxsteam.exe', 'SteamConnectorHelper.exe'):
        util.regedit_add(
            f'HKEY_CURRENT_USER\\Software\\Wine\\AppDefaults\\{exe}',
            'Version',
            'REG_SZ',
            'win10',
        )
