""" Lara Croft and the Guardian of Light
"""
#pylint: disable=C0103

from protonfixes import util


def main():
    """ LCGoL chokes on more than 12 cores
    """

    util.set_cpu_topology_limit(12)
