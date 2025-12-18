"""Escape From Tarkov
Install BattlEye Service - does not permit online play
"""

import os
import shutil
from pathlib import Path
from protonfixes import util
from protonfixes.logger import log

SERVICE_FLAG = "service_configured"

def main() -> None:
    util.install_battleye_runtime()
    util.protontricks('dotnet48')
    util.protontricks('vcrun2022')
    util.protontricks('dotnetdesktop6')
    util.protontricks('dotnetdesktop8')

    install_battleye_service()


def install_battleye_service() -> None:
    battleye_install = os.path.join(
        util.protonprefix(),
        'drive_c/Program Files (x86)/Common Files/BattlEye/',
    )
    os.makedirs(battleye_install, exist_ok=True)

    log.info("Checking if BattlEye Service is installed")
    if not os.path.exists(os.path.join(battleye_install, SERVICE_FLAG)):
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

        Path(os.path.join(battleye_install, SERVICE_FLAG)).touch()

    if not os.path.exists(os.path.join(battleye_install, "BEService_x64.exe")):
        log.info("Installing BattlEye Service")

        sources = [
            os.path.join(util.get_game_install_path(), 'build/BattlEye/'), # Steam
            os.path.join(util.protonprefix() , 'drive_c/Battlestate Games/Escape from Tarkov/BattlEye/'), # BsgLauncher
        ]
        battleye_source = None

        for source in sources:
            if os.path.exists(source):
                battleye_source = source
                break

        if battleye_source is None:
            return

        shutil.copytree(battleye_source, battleye_install, dirs_exist_ok=True)

        log.info("Installed BattlEye Service")
