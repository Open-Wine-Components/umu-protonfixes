""" Dragon Star Varnir
"""
#pylint: disable=C0103
from protonfixes import util


def main():
    """ Dragon Star Varnir fix
    """
    # Fixes the startup process.
    util.set_environment('WINEDLLOVERRIDES','xactengine3_7=n')
