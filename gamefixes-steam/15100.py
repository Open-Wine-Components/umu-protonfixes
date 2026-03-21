"""Assassin's Creed 1"""

from protonfixes import util


def main() -> None:
    util.set_cpu_topology_limit(31)

