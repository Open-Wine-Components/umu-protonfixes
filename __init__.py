"""Starts the protonfix module and runs fixes after pre-flight-checks"""

import os
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path
from typing import Callable, Optional

from . import fix
from .logger import log
from .upscalers import setup_upscalers
from .utilities import (
    setup_frame_rate,
    setup_local_shader_cache,
    setup_mount_drives,
    winetricks,
)

sys.path.insert(
    0,
    f'{os.path.dirname(os.path.realpath(__file__))}/_vendor',  # noqa: PTH120
)

bin_dir: str = f'{os.path.dirname(os.path.realpath(__file__))}/files/bin'
i386_lib_dir: str = (
    f'{os.path.dirname(os.path.realpath(__file__))}/files/lib/i386-linux-gnu'
)
x86_64_lib_dir: str = (
    f'{os.path.dirname(os.path.realpath(__file__))}/files/lib/x86_64-linux-gnu'
)
aarch64_lib_dir: str = (
    f'{os.path.dirname(os.path.realpath(__file__))}/files/lib/aarch64-linux-gnu'
)


# This is needed for protonfixes
os.environ['PROTON_DLL_COPY'] = '*'


class _ZenityWaitDialog:
    def __init__(self, text: str, title: str = 'ProtonFixes') -> None:
        self._text = text
        self._title = title
        self._proc = None  # type: Optional[subprocess.Popen]
        self._stop_evt = threading.Event()
        self._thread = None  # type: Optional[threading.Thread]
        self._tmp_cfg = None  # type: Optional[tempfile.TemporaryDirectory]

    def _make_env(self) -> Optional[dict[str, str]]:
        env = os.environ.copy()
        env['GTK_CSD'] = '1'

        # Only try GUI if we actually have a display
        if not env.get('DISPLAY') and not env.get('WAYLAND_DISPLAY'):
            return None

        # Create a temporary GTK config so zenity uses our colors.
        # GTK3 reads: $XDG_CONFIG_HOME/gtk-3.0/gtk.css
        self._tmp_cfg = tempfile.TemporaryDirectory(prefix='protonfixes-gtk-')
        cfg_root = Path(self._tmp_cfg.name)
        gtk_dir = cfg_root / 'gtk-3.0'
        gtk_dir.mkdir(parents=True, exist_ok=True)

        # Window bg: #171d25
        # Button + progress "status bar": #292e36
        # Text: white
        css = """
        window, dialog, box {
            background-color: #171d25;
        }

        /* The outer “frame” node GTK draws for CSD windows */
        decoration {
        background-color: #171d25;
        border: 1px solid #292e36;
        box-shadow: none;
        }

        /* Titlebar / headerbar */
        headerbar.titlebar {
        background-color: #171d25;
        color: #171d25;
        border-bottom: 1px solid #292e36;
        box-shadow: none;
        }

        headerbar.titlebar label {
        color: #ffffff;
        }

        /* Titlebar buttons (close/min/max) – if present */
        headerbar.titlebar button.titlebutton {
        background-color: #292e36;
        color: #000000;
        border: 1px solid #292e36;
        box-shadow: none;
        }

        headerbar.titlebar button.titlebutton:hover {
        background-color: #292e36;
        }

        /* Labels/text */
        label, text {
            color: #ffffff;
        }


        /* Progressbar ("status bar") */
        progressbar {
            color: #ffffff;
        }

        progressbar trough {
            background-color: #292e36;

            /* border / outline */
            border-color: #292e36;
            border-style: solid;
            border-width: 1px;

            /* optional: match the flat look */
            border-radius: 0;
            box-shadow: none;
        }

        progressbar progress {
            background-color: #292e36;
            border-radius: 0;
            box-shadow: none;
        }

        progressbar text {
            color: #ffffff;
        }
        """
        (gtk_dir / 'gtk.css').write_text(css, encoding='utf-8')

        env['XDG_CONFIG_HOME'] = str(cfg_root)
        return env

    def _start_one(self) -> Optional[subprocess.Popen]:
        env = self._make_env()
        if not env:
            return None  # no display; skip

        cmd = [
            'zenity',
            '--progress',
            '--pulsate',
            '--no-cancel',
            '--auto-close',
            '--title=' + self._title,
            '--text=' + self._text,
            '--width=420',
        ]

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

        # Best-effort: remove window decorations (X11/XWayland only)
        self._try_remove_decorations()

        return proc

    def _try_remove_decorations(self) -> None:
        # Only works on X11/XWayland
        env = os.environ
        if not env.get('DISPLAY'):
            return

        if subprocess.call(['sh', '-lc', 'command -v xprop >/dev/null 2>&1']) != 0:
            return
        if subprocess.call(['sh', '-lc', 'command -v xwininfo >/dev/null 2>&1']) != 0:
            return

        for _ in range(50):
            try:
                out = subprocess.check_output(
                    ['xwininfo', '-name', self._title],
                    stderr=subprocess.DEVNULL,
                ).decode('utf-8', 'ignore')

                wid = None
                for line in out.splitlines():
                    line = line.strip()
                    if line.lower().startswith('window id:'):
                        wid = line.split()[2]
                        break
                if not wid:
                    time.sleep(0.1)
                    continue

                # 1) Tell WM "no decorations" (Motif hints)
                subprocess.call(
                    [
                        'xprop',
                        '-id',
                        wid,
                        '-f',
                        '_MOTIF_WM_HINTS',
                        '32c',
                        '-set',
                        '_MOTIF_WM_HINTS',
                        '2, 0, 0, 0, 0',
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                # 2) Mark as SPLASH (many WMs won’t decorate splash windows)
                subprocess.call(
                    [
                        'xprop',
                        '-id',
                        wid,
                        '-set',
                        '_NET_WM_WINDOW_TYPE',
                        '_NET_WM_WINDOW_TYPE_SPLASH',
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                # 3) Optional: keep it out of taskbar/pager and above (cosmetic)
                subprocess.call(
                    [
                        'xprop',
                        '-id',
                        wid,
                        '-set',
                        '_NET_WM_STATE',
                        '_NET_WM_STATE_ABOVE,_NET_WM_STATE_SKIP_TASKBAR,_NET_WM_STATE_SKIP_PAGER',
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except Exception:
                time.sleep(0.1)

    def start(self) -> None:
        try:
            self._proc = self._start_one()
        except FileNotFoundError:
            self._proc = None
            return

        if not self._proc:
            return

        def _watch() -> None:
            while not self._stop_evt.is_set():
                if self._proc and self._proc.poll() is not None:
                    try:
                        self._proc = self._start_one()
                    except FileNotFoundError:
                        self._proc = None
                        return
                time.sleep(0.25)

        self._thread = threading.Thread(target=_watch, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_evt.set()

        if self._proc and self._proc.poll() is None:
            # Ask zenity to finish (so it auto-closes without showing OK)
            try:
                if self._proc.stdin:
                    self._proc.stdin.write(b'100\n')
                    self._proc.stdin.flush()
                    self._proc.stdin.close()
            except Exception:
                pass

            # Give it a moment to exit cleanly
            try:
                self._proc.wait(timeout=1.0)
            except Exception:
                # Fallback: kill it
                try:
                    self._proc.terminate()
                except Exception:
                    pass

        if self._thread:
            self._thread.join(timeout=1.0)

        if self._tmp_cfg:
            self._tmp_cfg.cleanup()
            self._tmp_cfg = None


def check_conditions() -> bool:
    """Determine, if the actual game was executed and protonfixes isn't deactivated.

    Returns:
        bool: True, if the fix should be executed.

    """
    return (
        len(sys.argv) >= 1
        and 'STEAM_COMPAT_DATA_PATH' in os.environ
        and 'PROTONFIXES_DISABLE' not in os.environ
        and 'waitforexitandrun' in sys.argv[1]
    )


def check_iscriptevaluator() -> bool:
    """Determine, if we were invoked while running "iscriptevaluator.exe".

    Returns:
        bool: True, if we were invoked while running "iscriptevaluator.exe".

    """
    return len(sys.argv) >= 3 and 'iscriptevaluator.exe' in sys.argv[2]


def setup(
    env: dict,
    bin_path_var: str,
    lib_path_var: str,
    func: Callable[[dict, str, str, str], None],
) -> None:
    """Setup PATH and LD_LIBRARY_PATH to include protonfixes's binary and library paths"""
    func(env, bin_path_var, bin_dir, ':')
    func(env, lib_path_var, f'{x86_64_lib_dir}:{aarch64_lib_dir}:{i386_lib_dir}', ':')


def execute() -> None:
    """Execute protonfixes"""
    if check_iscriptevaluator():
        log.debug('Skipping fix execution. We are running "iscriptevaluator.exe".')
    elif not check_conditions():
        log.warn('Skipping fix execution. We are probably running a unit test.')
    else:
        dialog = _ZenityWaitDialog('Installing Game-Specific fixes, please wait...')
        try:
            dialog.start()
            fix.main()

        except Exception:
            sys.stderr.write('ProtonFixes ' + traceback.format_exc())
            sys.stderr.flush()

        finally:
            dialog.stop()


__all__ = [
    'setup',
    'execute',
    'setup_frame_rate',
    'setup_local_shader_cache',
    'setup_mount_drives',
    'setup_upscalers',
    'winetricks',
]
