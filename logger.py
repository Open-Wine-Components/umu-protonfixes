"""Simple logging to stdout the same way Proton does"""

import os
import sys


class Log:
    """Log to stderr for steam dumps"""

    def __init__(self) -> None:  # noqa: D107
        self.pfx = 'ProtonFixes[' + str(os.getpid()) + '] '
        self.colors = {
            'RESET': '\u001b[0m',
            'INFO': '\u001b[34m',
            'WARN': '\u001b[33m',
            'CRIT': '\u001b[31m',
            'DEBUG': '\u001b[35m',
        }

    def __call__(self, msg: str) -> None:
        """Allows the Log instance to be called directly"""
        self.log(msg)

    def log(self, msg: str = '', level: str = 'INFO') -> None:
        """Prints the log message to stdout the same way as Proton"""
        pfx = self.pfx + level + ': '
        color = self.colors[level]
        reset = self.colors['RESET']
        logtext = pfx + str(msg) + os.linesep
        fulltext = color + pfx + str(msg) + reset + os.linesep
        sys.stderr.write(fulltext if os.isatty(sys.stderr.fileno()) else logtext)
        sys.stderr.flush()
        with open('/tmp/protonfixes_test.log', 'a', 1, encoding='utf-8') as testfile:
            testfile.write(logtext)

    def info(self, msg: str) -> None:
        """Wrapper for printing info messages"""
        self.log(msg, 'INFO')

    def warn(self, msg: str) -> None:
        """Wrapper for printing warning messages"""
        self.log(msg, 'WARN')

    def crit(self, msg: str) -> None:
        """Wrapper for printing critical messages"""
        self.log(msg, 'CRIT')

    def debug(self, msg: str) -> None:
        """Wrapper for printing debug messages"""
        if 'DEBUG' in os.environ:
            self.log(msg, 'DEBUG')


log = Log()
