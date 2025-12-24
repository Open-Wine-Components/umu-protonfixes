"""Implements a waiting dialog using zenity"""

import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional


class ZenityWaitDialog:
    """Implements a waiting dialog using zenity"""

    def __init__(self, text: str, title: str = 'ProtonFixes') -> None:
        """Initialize zenity dialog

        :param text: the message displayed in the dialog window
        :type text: str

        :param title: the title of the dialog window
        ;type title; str
        """
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

        return proc

    def start(self) -> None:
        """Show the wait dialog"""
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
        """Hide the wait dialog"""
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


__all__ = ['ZenityWaitDialog']
