"""X-Blades"""

from protonfixes import util


def main() -> None:
    """The launcher won't start the game, so it needs to be skipped for the game to run."""
    util.replace_command('launcher\\.exe$', 'xblades.exe')
