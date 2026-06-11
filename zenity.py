"""Implements a waiting dialog using zenity"""

import os
import subprocess
import threading
import time
from typing import Optional


class ZenityWaitDialog:
    """Implements a waiting dialog using zenity"""

    def __init__(self, text: str, title: str = 'ProtonFixes') -> None:
        """Initialize zenity dialog

        :param text: the message displayed in the dialog window
        :type text: str

        :param title: the title of the dialog window
        :type title: str
        """
        self._text = text
        self._title = title
        self._proc = None  # type: Optional[subprocess.Popen]
        self._stop_evt = threading.Event()
        self._thread = None  # type: Optional[threading.Thread]

    def _make_env(self) -> Optional[dict[str, str]]:
        env = os.environ.copy()
        env['GTK_CSD'] = '1'

        # Only try GUI if we actually have a display
        if not env.get('DISPLAY') and not env.get('WAYLAND_DISPLAY'):
            return None

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


__all__ = ['ZenityWaitDialog']
