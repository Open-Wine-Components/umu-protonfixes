""" Game fix for Outlaws + A Handful of Missions
"""
#pylint: disable=C0103
#
from protonfixes import util

def main():
    # Override ddraw (cutscenes+menu perf) and WinMM (Music)
    util.set_environment('WINEDLLOVERRIDES', 'ddraw=n,b;winmm=n,b')
