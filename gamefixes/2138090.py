""" Atelier Marie Remake: The Alchemist of Salburg
Missing voices/sounds in cutscenes
Requires disabling the gstreamer protonaudioconverterbin plugin to get full audio in cutscenes.
fixed by Swish in Protondb
further stolen from marianoag by bitwolf
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.set_environment('GST_PLUGIN_FEATURE_RANK', 'protonaudioconverterbin:NONE')
