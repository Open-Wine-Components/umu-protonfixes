"""Game fix for VRChat."""

from protonfixes import util
from protonfixes.logger import log


PLUGIN_SOURCE = '''"""Keep VRChat's outdated yt-dlp compatible with YouTube."""

from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.extractor.youtube._base import INNERTUBE_CLIENTS


if "android" in INNERTUBE_CLIENTS:
    YoutubeIE._DEFAULT_CLIENTS = ("android",)
    YoutubeIE._DEFAULT_JSLESS_CLIENTS = ("android",)


def _is_h264(format_info):
    codec = (format_info.get("vcodec") or "").lower()
    return codec.startswith(("avc1", "avc", "h264"))


def _has_audio(format_info):
    return (format_info.get("acodec") or "").lower() not in ("", "none")


if "android" in YoutubeIE._DEFAULT_CLIENTS:
    _original_real_extract = YoutubeIE._real_extract

    if not getattr(_original_real_extract, "_ge_proton_vrchat_muxed", False):
        def _real_extract_muxed(self, url):
            info = _original_real_extract(self, url)
            formats = info.get("formats") or []
            muxed_h264 = [
                format_info for format_info in formats
                if _is_h264(format_info) and _has_audio(format_info)
            ]

            if muxed_h264:
                info["formats"] = muxed_h264
            else:
                # Preserve playback on videos without a muxed rendition,
                # even though those may still lack audio in VRChat.
                info["formats"] = [
                    format_info for format_info in formats
                    if _is_h264(format_info)
                    or ((format_info.get("vcodec") or "").lower() == "none"
                        and _has_audio(format_info))
                ]

            return info

        _real_extract_muxed._ge_proton_vrchat_muxed = True
        YoutubeIE._real_extract = _real_extract_muxed
'''


def main() -> None:
    """Install the yt-dlp compatibility plugin into the prefix."""
    plugin_path = (
        util.protonprefix()
        / 'drive_c/users/steamuser/AppData/Roaming/yt-dlp/plugins'
        / 'ge-proton-vrchat/yt_dlp_plugins/extractor/vrchat_visionos.py'
    )

    try:
        plugin_path.parent.mkdir(parents=True, exist_ok=True)
        if not plugin_path.exists() or plugin_path.read_text(
            encoding='utf-8'
        ) != PLUGIN_SOURCE:
            plugin_path.write_text(PLUGIN_SOURCE, encoding='utf-8')
    except OSError as error:
        log.warn(
            f"Failed to install VRChat yt-dlp plugin at '{plugin_path}': "
            f'{error}'
        )
