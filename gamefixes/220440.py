""" Game fix DMC Devil May Cry
    (Currently without controller)
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Needs dotnet40 """

    util.protontricks('dotnet40')
    util.protontricks('nocrashdialog')

#TODO Controllers fixes
