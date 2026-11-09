"""Game fix for Wolfenstein: The New Order"""

from protonfixes import util
from protonfixes.logger import log


def main() -> None:
    """Create cache directory in AppData Local to prevent crash on launch"""
    cache_dir = (
        util.protonprefix()
        / 'drive_c/users/steamuser/AppData/Local/MachineGames/Wolfenstein The New Order'
    )
    if not cache_dir.is_dir():
        log.info(f'Creating cache directory: {cache_dir}')
        cache_dir.mkdir(parents=True, exist_ok=True)
