"""Starts the protonfix module"""

import os
import sys

RUN_CONDITIONS = [
    'STEAM_COMPAT_DATA_PATH' in os.environ,
    'PROTONFIXES_DISABLE' not in os.environ,
    'waitforexitandrun' in sys.argv[1],
]

if all(RUN_CONDITIONS):
    import traceback
    from . import fix

    try:
        fix.main()

    # Catch any exceptions and print a traceback
    except:
        sys.stderr.write('ProtonFixes ' + traceback.format_exc())
        sys.stderr.flush()
