"""Game fix for Kabounce"""
from protonfixes import util


def main() -> None:
    """Disable OpenSSL code check for SHA extensions"""
    # Kabounce bundles OpenSSL 1.0.2, which is affected by the
    # OpenSSL SHA Crash bug, which causes the game to crash on
    # Intel 10th-gen and newer CPUs. This env disables the
    # problematic code path.
    # https://www.intel.com/content/www/us/en/developer/articles/troubleshooting/openssl-sha-crash-bug-requires-application-update.html
    util.set_environment('OPENSSL_ia32cap', ':~0x20000000')
