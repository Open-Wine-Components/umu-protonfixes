"""Colin McRae: DiRT"""

from protonfixes import util


def main() -> None:
    """The game crashes without limiting cores"""
    util.set_cpu_topology_limit(4)
