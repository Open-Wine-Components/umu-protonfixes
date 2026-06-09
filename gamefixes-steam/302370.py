"""Tex Murphy: Overseer
DgVoodoo for textures
"""

import os
import subprocess
from protonfixes import util


def main() -> None:
    if util.protontricks('dgvoodoo2'):
        syswow64 = os.path.join(
            util.protonprefix(), 'drive_c/windows/syswow64', 'dgvoodoo.conf'
        )
        subprocess.call(
            [f"sed -i '/[DirectX]/ {{/Resolution/s/max/unforced/}}' {syswow64}"],
            shell=True,
        )
