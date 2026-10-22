"""Game fix for Star Citizen"""

import os
from protonfixes import util

def main() -> None:
    # Keep the address range libcuda reserves in free of the game's huge allocations,
    # otherwise the Vulkan extensions DLSS needs fail to initialize
    util.set_environment('WINE_DISABLE_BOTTOM_UP_ALLOC', '1')

    # Satisfy check for the existence of these dlls when trying to initialize ngx
    # Copy an existing DLL to these three names
    env_path = os.path.join(util.protonprefix(), 'drive_c', 'windows', 'system32')
    dest_files = ['cryptbase.dll', 'devobj.dll', 'drvstore.dll']
    for file in dest_files:
        link_path = os.path.join(env_path, file)
        if not os.path.isfile(link_path):
            os.symlink('security.dll', link_path)

    # RSI Launcher depends on powershell
    util.protontricks('powershell')

    # Prevents Error code 3221225477
    util.protontricks('vcrun2022')

    # New launcher needs dotnet48
    util.protontricks('dotnet48')

    # Reset version to win10
    util.protontricks('win10')

    # Prevent RSI Launcher install and update from hanging indefinitely
    util.winedll_override('dxwebsetup.exe', util.OverrideOrder.DISABLED)
    util.winedll_override('dotNetFx45_Full_setup.exe', util.OverrideOrder.DISABLED)
