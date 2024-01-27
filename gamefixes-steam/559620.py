""" Game fix for Outlaws + A Handful of Missions
"""
#pylint: disable=C0103
#
from protonfixes import util

def main():
    # Override ddraw (cutscenes+menu perf) and WinMM (Music)
    util.winedll_override('ddraw', 'n,b')
    util.winedll_override('winmm', 'n,b')
