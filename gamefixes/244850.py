""" Game fix for Space Engineers
"""

# pylint: disable=C0103

from protonfixes import util


def main():
    # This requires Proton 5.0 installed
    util.install_dotnet('dotnet48')
    util.append_argument('-skipintro')
