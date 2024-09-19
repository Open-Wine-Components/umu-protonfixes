"""Game fix for Star Citizen"""

from protonfixes import util


def main() -> None:
    """EAC Workaround"""
    # eac workaround
    util.set_environment('EOS_USE_ANTICHEATCLIENTNULL', '1')

    # RSI Launcher depends on powershell
    util.protontricks('powershell')
