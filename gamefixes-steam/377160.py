"""Game fix for Fallout 4"""

import os
from protonfixes import util


def main() -> None:
    """Run script extender if it exists."""
    # Fixes the startup process.
    if os.path.isfile(os.path.join(os.getcwd(), 'f4se_loader.exe')):
        util.replace_command('Fallout4Launcher.exe', 'f4se_loader.exe')
