"""Game fix for Warhammer 40,000: Darktide"""

from protonfixes import util


def main() -> None:
    """Bypass the launcher to prevent bug: the game would launch as a background process with audio only."""
    util.replace_command('launcher/Launcher.exe', 'binaries/Darktide.exe')
    # EAC was removed from the game, the launcher launches the game with these options by default now even though -eac-untrusted does nothing
    util.append_argument('-eac-untrusted --bundle-dir ../bundle --ini settings')

