"""Game fix for Serious Sam 4"""

import os
import subprocess


def main() -> None:
    """Graphics API workaround"""
    if not os.path.isfile('UserCfg.lua.bak'):
        subprocess.call(['cp', 'UserCfg.lua', 'UserCfg.lua.bak'])

        # Assume UTF-8
        with open('UserCfg.lua', 'a+', encoding='utf-8') as f:
            f.write('sfx_strAPI = "OpenAL";')
