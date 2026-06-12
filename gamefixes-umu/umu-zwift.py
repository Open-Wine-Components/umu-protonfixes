"""Game fix for Zwift"""

import os
from protonfixes import util

# Necessary for dotnet installations
# see: https://github.com/Open-Wine-Components/umu-protonfixes/pull/557
def early() -> None:
    os.environ['PROTON_DLL_COPY'] = '*'

def main() -> None:
    util.protontricks('corefonts dotnet48 d3dcompiler_47 webview2')
