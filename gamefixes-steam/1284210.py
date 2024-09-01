"""Game fix for Guild Wars 2"""

import os
from protonfixes import util


def main() -> None:
    """GW2 add NOSTEAM option."""
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('-provider', '')
