""" Game fixes Call of Juarez: Gunslinger
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ installs wmp11
    """
    # Fixes missing cutscenes
    util.protontricks('wmp11')
    # Seems to choke on more than 32 cores, needs testing
    util.set_cpu_topology_limit(31)
