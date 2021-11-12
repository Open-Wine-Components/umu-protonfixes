""" Ship Graveyard Simulator
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ needs builtin vulkan-1
    """

    util.set_environment('WINEDLLOVERRIDES','vulkan-1=b')


