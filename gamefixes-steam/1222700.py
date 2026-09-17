"""Game fix for A Way Out"""
from protonfixes import util


def main() -> None:
    """Work around UE4 OpenSSL crash on Intel 10th-gen and newer CPUs."""
    # UE4.13-4.21 bundles OpenSSL 1.0, which crashes on CPUs with SHA
    # extensions. This disables the buggy code path.
    # https://github.com/ValveSoftware/Proton/issues/5830
    util.set_environment('OPENSSL_ia32cap', ':~0x20000000')
