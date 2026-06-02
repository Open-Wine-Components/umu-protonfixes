"""Setup for all GOG games"""

from protonfixes import util


def main() -> None:
    util.set_environment('OPENSSL_ia32cap', ':~0x20000000')
