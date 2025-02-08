"""Hard Truck Apocalypse: Rise of Clans"""

from protonfixes import util


def main() -> None:
    """Won't start at 32 or more cores."""
    util.set_cpu_topology_limit(31)
