""" Shin Megami Tensei III Nocturne HD Remaster
Missing voices/sounds in cutscenes
Requires disabling the gstreamer protonaudioconverterbin plugin to get full audio in cutscenes.
fixed Persona 5 Strikers by Swish in Protondb
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.disable_protonmediaconverter()
