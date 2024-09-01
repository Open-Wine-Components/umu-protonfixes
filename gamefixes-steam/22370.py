"""Game fix for Fallout 3"""

import os
from protonfixes import util


def main() -> None:
    """Run script extender if it exists."""

    if os.path.isfile(os.path.join(os.getcwd(), 'fose_loader.exe')):
        util.replace_command('FalloutLauncher.exe', 'fose_loader.exe')
