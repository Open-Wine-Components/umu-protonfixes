"""UNCHARTED: Legacy of Thieves Collection"""

from protonfixes import util


def main() -> None:
    """The game chokes on more than 16 cores"""
    util.set_cpu_topology_limit(16)
