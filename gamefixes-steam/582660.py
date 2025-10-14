"""Game fix for Black Desert Online"""

import os
from protonfixes import util


def main() -> None:
    """Black Desert Online add NOSTEAM option."""
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('--steam', '')
    # Needed for Launcher
    util.set_environment('WINE_DISABLE_KERNEL_WRITEWATCH', '1')
    configpath = os.path.join(
        util.protonprefix(),
        'drive_c/users/steamuser/My Documents/Black Desert',
    )
    if not os.path.exists(configpath):
        os.makedirs(configpath)
    configgame = os.path.join(configpath, 'GameOptionLauncher.txt')
    if not os.path.isfile(configgame):
        with open(configgame, 'w+', encoding='utf-8') as f:
            f.write('launcherGpu = 0\nlauncherOffScreen = 0')
