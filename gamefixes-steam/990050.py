"""Death end re;Quest"""

from protonfixes import util


def main() -> None:
    """Fixes performance and random crashings"""
    util.set_cpu_topology_limit(2)
