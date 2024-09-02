"""Far Cry Blood Dragon"""

from protonfixes import util


def main() -> None:
    """dx11 version is broken"""
    util.set_cpu_topology_limit(24)
