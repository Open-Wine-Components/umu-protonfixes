""" Lara Croft and the Guardian of Light
"""
#pylint: disable=C0103

from protonfixes import util
import multiprocessing


def main():
    """ LCGoL chokes on more than 12 cores
    """

    if multiprocessing.cpu_count() > 24:
        util.set_environment('WINE_CPU_TOPOLOGY', '12:0,1,2,3,4,5,6,7,8,9,10,11')

