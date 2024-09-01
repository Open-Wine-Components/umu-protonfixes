"""Game fix for FFXIV"""

import os
from protonfixes import util


def main():
    """FFXIV add NOSTEAM option."""
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('-issteam', '')
