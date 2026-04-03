"""Game fix for Gray Zone Warfare

Sets specific cache files to read-only to prevent the game from modifying them
after first launch, which would invalidate Easy Anti-Cheat hashes.
"""

import stat
from pathlib import Path

from protonfixes import util
from protonfixes.logger import log


def main() -> None:
    """Set EAC-validated cache files to read-only"""
    game_dir = Path(util.get_game_install_path())
    cache_dir = game_dir / "GZW/Content/SKALLA/PrebuildWorldData/World/cache"

    files = [
        "0xb9af63cee2e43b6c_0x3cb3b3354fb31606.dat",
        "0xaf497c273f87b6e4_0x7a22fc105639587d.dat",
    ]

    for filename in files:
        filepath = cache_dir / filename
        if filepath.is_file():
            # Remove write permission for owner, group, and others
            current_mode = filepath.stat().st_mode
            readonly_mode = current_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            if current_mode != readonly_mode:
                log.info(f'Setting "{filepath.name}" to read-only.')
                filepath.chmod(readonly_mode)
        else:
            log.info(f'Cache file "{filepath.name}" not found, skipping.')
