"""Game fix for FFXIV"""

import os
import re
from protonfixes import util


def _is_env_one(name: str) -> bool:
    # Only treat an explicit "1" as enabled (per your requirement)
    return os.environ.get(name, "") == "1"


def main() -> None:
    """FFXIV add NOSTEAM option."""
    # Fixes the startup process.
    if 'NOSTEAM' in os.environ:
        util.replace_command('-issteam', '')

    # disable new character intro cutscene to prevent black screen loop
    configpath = os.path.join(
        util.protonprefix(),
        'drive_c/users/steamuser/My Documents/My Games/FINAL FANTASY XIV - A Realm Reborn'
    )
    if not os.path.exists(configpath):
        os.makedirs(configpath)

    configgame = os.path.join(configpath, 'FFXIV_BOOT.cfg')

    # Only do the WebView2RuntimeInvalid change when Wayland env is explicitly "1"
    if _is_env_one("PROTON_USE_WAYLAND") or _is_env_one("PROTON_ENABLE_WAYLAND"):
        if not os.path.isfile(configgame):
            # Create a minimal file with the setting forced to 1
            with open(configgame, "w", encoding="utf-8") as f:
                f.write(
                    "<FINAL FANTASY XIV Config File>\n\n"
                    "<Version>\n"
                    "WebView2RuntimeInvalid 1\n"
                )
            return

        # If the file exists: set WebView2RuntimeInvalid to 1 (idempotent)
        with open(configgame, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        new_content = re.sub(
            r'(?m)^(WebView2RuntimeInvalid)\s+\d+\s*$',
            r'\1 1',
            content
        )

        if new_content == content:
            # Key not present: append it
            if not new_content.endswith("\n"):
                new_content += "\n"
            new_content += "WebView2RuntimeInvalid 1\n"

        with open(configgame, "w", encoding="utf-8") as f:
            f.write(new_content)
