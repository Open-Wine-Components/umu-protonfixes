"""Game fix for The Sims 4"""

import os
import subprocess

from protonfixes import util
from protonfixes.logger import log

_EA_DESKTOP = os.path.join('drive_c', 'Program Files', 'Electronic Arts', 'EA Desktop')

_INSTALLER = os.path.join(
    '__Installer', 'Origin', 'redist', 'internal', 'EAappInstaller.exe'
)


def main() -> None:
    """Install the EA App, which registers the link2ea:// handler"""
    # Steam launches this game as a link2ea:// URI instead of an executable, and
    # only the EA App registers that scheme. The game's install script is meant
    # to install it, but it runs the bundled EAappInstaller.exe without a
    # display mode, so the installer waits on a window nobody sees in Game Mode.
    # Wine then starts, finds no handler for the URI and exits 0 with no window
    # and no crash. Installing it with /quiet registers link2ea and sets the
    # HasRunStringKey the install script checks, so Steam stops retrying.
    prefix = util.protonprefix()

    if os.path.isdir(os.path.join(prefix, _EA_DESKTOP)):
        return

    installer = os.path.join(util.get_game_install_path(), _INSTALLER)

    if not os.path.isfile(installer):
        log.warn(f'EA App installer not found at "{installer}"')
        return

    env = dict(util.protonmain.g_session.env)
    env['WINEPREFIX'] = str(prefix)
    env['WINE'] = util.protonmain.g_proton.wine_bin
    env['WINELOADER'] = util.protonmain.g_proton.wine_bin
    env['WINESERVER'] = util.protonmain.g_proton.wineserver_bin
    env['LD_PRELOAD'] = ''

    log.info('Installing the EA App')
    retc = subprocess.call(
        [env['WINE'], installer, '/quiet', 'EAX_LAUNCH_CLIENT=0', 'IGNORE_INSTALLED=1'],
        env=env,
    )

    if retc != 0:
        log.warn(f'EA App installer exited with status {retc}')
        return

    if not os.path.isdir(os.path.join(prefix, _EA_DESKTOP)):
        log.warn('EA App installer reported success but installed nothing')
