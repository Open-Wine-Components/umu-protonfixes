"""Game fix for Star Citizen"""

import os
from protonfixes import util


def main() -> None:
    # patch libcuda to workaround crashes related to DLSS
    # See: https://github.com/jp7677/dxvk-nvapi/issues/174#issuecomment-2227462795
    patched = util.patch_libcuda()
    if patched:
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

    # RSI Launcher animation
    util.winedll_override('libglesv2', util.OverrideOrder.BUILTIN)
