"""Escape From Tarkov
Install BattlEye Service - does not permit online play
"""

import os
import glob
import shutil
from protonfixes import util

def main() -> None:
    util.install_battleye_runtime()
    util.protontricks('dotnet48')
    util.protontricks('vcrun2022')
    util.protontricks('dotnetdesktop6')
    util.protontricks('dotnetdesktop8')

    game_dir = glob.escape(util.get_game_install_path())

    battleye_source = os.path.join(
        game_dir,
        'build/BattlEye/',
    )

    battleye_install = os.path.join(
        util.protonprefix(),
        'drive_c/Program Files (x86)/Common Files/BattlEye/',
    )

    if not os.path.exists(battleye_install):
        # Setup BattlEye Service for the game to run
        # This is only to get past the launcher and does not enable online play

        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'DisplayName',
            'REG_SZ',
            'BattlEye Service',
        )
        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'ErrorControl',
            'REG_DWORD',
            '1',
        )
        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'ObjectName',
            'REG_SZ',
            'LocalSystem',
        )
        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'ImagePath',
            'REG_SZ',
            'C:\\Program Files (x86)\\Common Files\\BattlEye\\BEService_x64.exe',
        )
        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'PreshutdownTimeout',
            'REG_DWORD',
            '180000',
        )
        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'Start',
            'REG_DWORD',
            '2',
        )

        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'Type',
            'REG_DWORD',
            '16',
        )

        util.regedit_add(
            'HKLM\\System\\CurrentControlSet\\Services\\BEService',
            'WOW64',
            'REG_DWORD',
            '1',
        )

        shutil.copytree(battleye_source, battleye_install, dirs_exist_ok=True)
