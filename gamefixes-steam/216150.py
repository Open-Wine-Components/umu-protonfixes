"""Game fix for MapleStory"""

import os
import subprocess

from protonfixes import util
from protonfixes.logger import log

_REG_SETTINGS = r"""Windows Registry Editor Version 5.00

; Alt-tab input fix - prevent Wine from stealing focus on alt-tab
[HKEY_CURRENT_USER\Software\Wine\X11 Driver]
"UseTakeFocus"="N"

; DirectInput raw input events for keyboard/mouse
[HKEY_CURRENT_USER\Software\Wine\DirectInput]
"UseLinuxInputEvents"="Y"
"KeyboardUseNonExclusive"="Y"
"MouseUseNonExclusive"="Y"

[HKEY_CURRENT_USER\Software\Wine\X11 Driver]
"Grab"="N"
"GrabFullscreen"="N"
"UseLinuxInputEvents"="Y"

; Report Windows 10 for the launcher/anti-cheat handoff
[HKEY_CURRENT_USER\Software\Wine\AppDefaults\MapleStory.exe]
"Version"="win10"

[HKEY_CURRENT_USER\Software\Wine\AppDefaults\nxsteam.exe]
"Version"="win10"

[HKEY_CURRENT_USER\Software\Wine\AppDefaults\SteamConnectorHelper.exe]
"Version"="win10"

; Nexon launcher protocol handler
[HKEY_CURRENT_USER\Software\Nexon Launcher]
"Install Directory"="C:\\Nexon\\Launcher"
"Region"="1"
"User Data"="{\"setup-id\":\"372e7640-20f4-419c-ada0-4ad0d76c33d9\",\"time\":1748271149}"

[HKEY_LOCAL_MACHINE\Software\Classes\Applications\nexon_launcher.exe\shell\open]
"FriendlyAppName"="Nexon Launcher"

[HKEY_LOCAL_MACHINE\Software\Classes\nxl]
@="URL:nxl protocol"
"URL Protocol"=""

[HKEY_LOCAL_MACHINE\Software\Classes\nxl\DefaultIcon]
@="C:\\Nexon\\Launcher\\nexon_launcher.exe"

[HKEY_LOCAL_MACHINE\Software\Classes\nxl\shell]
@=""

[HKEY_LOCAL_MACHINE\Software\Classes\nxl\shell\open]
@=""
"Friendly App Name"="Nexon Launcher"

[HKEY_LOCAL_MACHINE\Software\Classes\nxl\shell\open\command]
@="\"C:\\Nexon\\Launcher\\nexon_launcher.exe\" \"%1\""

[HKEY_LOCAL_MACHINE\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Nexon Nexon Launcher]
"DisplayIcon"="\"C:\\Nexon\\Launcher\\logo.ico\""
"DisplayName"="Nexon Launcher"
"DisplayVersion"="2.3.0"
"EstimatedSize"=dword:00002b48
"HelpLink"="\"http://www.nexon.net/legal/terms-of-use/\""
"InstallLocation"="\"C:\\Nexon\\Launcher\""
"NoModify"=dword:00000001
"NoRepair"=dword:00000001
"Publisher"="Nexon"
"QuietUninstallString"="\"C:\\Nexon\\Launcher\\uninstall.exe\" /S"
"UninstallString"="\"C:\\Nexon\\Launcher\\uninstall.exe\""
"URLInfoAbout"="\"http://www.nexon.net\""
"URLUpdateInfo"="\"http://www.nexon.net\""
"VersionMajor"=dword:00000002
"VersionMinor"=dword:00000003

; Direct3D settings
[HKEY_CURRENT_USER\Software\Wine\Direct3D]
"cb_access_map_w"=dword:00000001
"CSMT"="disabled"
"""


def main() -> None:
    """Apply MapleStory registry settings.

    Mirrors the known-working reference prefix:
    - X11 Driver UseTakeFocus=N, Grab=N, GrabFullscreen=N, UseLinuxInputEvents=Y
    - DirectInput UseLinuxInputEvents=Y, Keyboard/MouseUseNonExclusive=Y
    - AppDefaults Version=win10 for MapleStory.exe, nxsteam.exe,
      SteamConnectorHelper.exe
    - Nexon launcher nxl: protocol handler registration
    - Direct3D cb_access_map_w=1, CSMT=disabled

    Note: UseLinuxInputEvents requires the user to be in the system 'input'
    group (e.g. ``sudo usermod -aG input $USER``). This gamefix cannot
    perform that step - it only sets the registry keys.

    Note: this fix is necessary but not sufficient to launch MapleStory on
    Proton. The game additionally requires source-level patches:
    - kernelbase CharPrevA/CharPrevExA NULL-deref fix (Wine bug 59926)
    - win32u SPI_SETSTICKYKEYS/SPI_SETFILTERKEYS WINE_SPI_WARN (Wine bug 59927)
    """
    prefix = util.protonprefix()
    reg_file = os.path.join(str(prefix), 'drive_c', 'maplestory_settings.reg')
    with open(reg_file, 'w', encoding='ascii') as f:
        f.write(_REG_SETTINGS)
    env = dict(util.protonmain.g_session.env)
    env['WINEPREFIX'] = str(prefix)
    env['WINE'] = util.protonmain.g_proton.wine_bin
    env['WINELOADER'] = util.protonmain.g_proton.wine_bin
    env['WINESERVER'] = util.protonmain.g_proton.wineserver_bin
    log.info('Importing MapleStory registry settings')
    subprocess.call(
        ['wine', 'regedit', '/S', 'C:\\maplestory_settings.reg'],
        env=env,
    )
    os.unlink(reg_file)
