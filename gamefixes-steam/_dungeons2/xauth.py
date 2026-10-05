#!/usr/bin/env python3
"""Sign in with the user's own Microsoft account and cache Xbox tokens.

The browser login uses this game's Microsoft app id. Tokens are written
for the local runtime; they are never printed.
"""
import base64
import json
import os
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

CLIENT = "00000000497C1B94"
SCOPE = "service::user.auth.xboxlive.com::MBI_SSL"
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(HERE, "tokens.txt")
CODE_PATH = os.path.join(HERE, "login-code.txt")


class ProofKey:
    """P-256 key that signs Xbox auth requests and binds tokens to a device.

    Steam's Python has no cryptography module, so this uses the openssl
    CLI that ships in the runtime.
    """

    def __init__(self):
        fd, self.path = tempfile.mkstemp(suffix=".pem")
        os.close(fd)
        try:
            self._openssl("ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", self.path)
            point = self._openssl("ec", "-in", self.path, "-pubout", "-outform", "DER")[-64:]
        except Exception:
            self.close()
            raise
        b64 = lambda raw: base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
        self.jwk = {
            "kty": "EC",
            "x": b64(point[:32]),
            "y": b64(point[32:]),
            "crv": "P-256",
            "alg": "ES256",
            "use": "sig",
        }

    def _openssl(self, *args, data=None):
        return subprocess.run(
            ["openssl", *args], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        ).stdout

    @staticmethod
    def _ecdsa_rs(der):
        if not der or der[0] != 0x30:
            raise ValueError("openssl did not return a DER ECDSA signature")
        idx = 2 if der[1] < 0x80 else 2 + (der[1] & 0x7F)

        def take_int(pos):
            if der[pos] != 0x02:
                raise ValueError("DER signature is missing an integer")
            length = der[pos + 1]
            start = pos + 2
            value = int.from_bytes(der[start:start + length], "big")
            return value, start + length

        r, idx = take_int(idx)
        s, _ = take_int(idx)
        return r, s

    def signature(self, url, body):
        stamp = (int(time.time()) + 11644473600) * 10000000
        path = urllib.parse.urlsplit(url).path
        signed = (
            struct.pack(">I", 1)
            + b"\0"
            + struct.pack(">Q", stamp)
            + b"\0POST\0"
            + path.encode()
            + b"\0\0"
            + body
            + b"\0"
        )
        der = self._openssl("dgst", "-sha256", "-sign", self.path, data=signed)
        r, s = self._ecdsa_rs(der)
        raw = struct.pack(">I", 1) + struct.pack(">Q", stamp) + r.to_bytes(32, "big") + s.to_bytes(32, "big")
        return base64.b64encode(raw).decode()

    def close(self):
        try:
            os.unlink(self.path)
        except OSError:
            pass


def post(url, form=None, payload=None, key=None):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if key:
            headers["Signature"] = key.signature(url, data)
            headers["x-xbl-contract-version"] = "1"
    else:
        data = urllib.parse.urlencode(form).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"error": body[:300]}
        parsed["_status"] = exc.code
        return parsed


def jwt_exp(token):
    try:
        if ";" in token:
            token = token.rsplit(";", 1)[1]
        part = token.split(".")[1]
        part += "=" * (-len(part) % 4)
        data = json.loads(base64.urlsafe_b64decode(part))
        return int(data.get("exp", 0))
    except Exception:
        return 0


def repair_stored_exp():
    if not os.path.isfile(TOKEN_PATH):
        return
    lines = []
    values = {}
    with open(TOKEN_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            lines.append(line.rstrip("\n"))
            if "=" in line:
                key, value = line.rstrip("\n").split("=", 1)
                values[key] = value
    if int(values.get("exp") or "0") > time.time() + 120:
        return
    exp = 0
    for key in ("xbox", "mc", "playfab"):
        got = jwt_exp(values.get(key, ""))
        if got:
            exp = min(exp, got) if exp else got
    if not exp:
        return
    replaced = False
    for i, line in enumerate(lines):
        if line.startswith("exp="):
            lines[i] = "exp=%s" % exp
            replaced = True
    if not replaced:
        lines.insert(0, "exp=%s" % exp)
    write_tokens([(line.split("=", 1)[0], line.split("=", 1)[1] if "=" in line else "") for line in lines])


def cached_ok():
    if not os.path.isfile(TOKEN_PATH):
        return False
    exp = 0
    playfab = False
    with open(TOKEN_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("exp="):
                exp = int(line[4:].strip() or "0")
            elif line.startswith("playfab=XBL"):
                playfab = True
    return playfab and exp > time.time() + 120


def rps_ticket(access):
    if access.startswith("t=") or access.startswith("d="):
        return access
    if access.startswith("eyJ"):
        return "d=" + access
    return "t=" + access


def xbox_user(access):
    result = post("https://user.auth.xboxlive.com/user/authenticate", payload={
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": rps_ticket(access),
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    })
    if "Token" not in result:
        raise SystemExit("Xbox user auth failed: %s" % result.get("XErr", result.get("error")))
    return result["Token"]


def device_token(key):
    result = post("https://device.auth.xboxlive.com/device/authenticate", payload={
        "Properties": {
            "AuthMethod": "ProofOfPossession",
            "Id": "{%s}" % uuid.uuid4(),
            "DeviceType": "Win32",
            "Version": "10.0.26100",
            "ProofKey": key.jwk,
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }, key=key)
    if "Token" not in result:
        raise SystemExit("Xbox device auth failed: %s" % result.get("XErr", result.get("error", result.get("_status"))))
    return result["Token"]


def xsts(user_token, relying, device, key):
    # PlayFab rejects tokens without a device claim ("Unidentified DeviceType").
    result = post("https://xsts.auth.xboxlive.com/xsts/authorize", payload={
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [user_token],
            "DeviceToken": device,
        },
        "RelyingParty": relying,
        "TokenType": "JWT",
    }, key=key)
    if "Token" not in result:
        return None, result.get("XErr", result.get("error"))
    return result, None


def auth_header(doc):
    claim = doc["DisplayClaims"]["xui"][0]
    return "XBL3.0 x=%s;%s" % (claim["uhs"], doc["Token"]), claim


def write_tokens(fields):
    tmp = TOKEN_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        for key, value in fields:
            handle.write("%s=%s\n" % (key, value))
    os.chmod(tmp, 0o600)
    os.replace(tmp, TOKEN_PATH)


def desktop_env():
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    env.setdefault("XDG_RUNTIME_DIR", "/run/user/%s" % os.getuid())
    return env


def show_code(url, code):
    with open(CODE_PATH, "w", encoding="utf-8") as handle:
        handle.write(url + "\n" + code + "\n")
    env = desktop_env()
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.Popen([opener, url], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass
    text = "Sign in with your Microsoft account.\n\nOpen %s\nCode: %s" % (url, code)
    if os.path.exists("/usr/bin/zenity"):
        subprocess.Popen(
            ["zenity", "--info", "--title=Minecraft Dungeons II sign-in", "--text", text, "--width=420"],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )


def poll_msa(device_code, interval, expires_in):
    deadline = time.time() + max(30, expires_in - 5)
    while time.time() < deadline:
        time.sleep(max(int(interval), 5))
        result = post("https://login.live.com/oauth20_token.srf", form={
            "client_id": CLIENT,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        })
        if "access_token" in result:
            return result
        err = result.get("error", "")
        if err == "slow_down":
            interval = int(interval) + 5
            continue
        if err == "authorization_pending":
            continue
        raise SystemExit("Microsoft login failed: %s" % (result.get("error_description") or err or result.get("_status")))
    raise SystemExit("Microsoft login timed out")


def refresh_msa(refresh):
    result = post("https://login.live.com/oauth20_token.srf", form={
        "client_id": CLIENT,
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "scope": SCOPE,
    })
    if "access_token" not in result:
        return None
    return result


def load_refresh():
    if not os.path.isfile(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("refresh="):
                return line[len("refresh="):].rstrip("\n")
    return None


def finish(msa):
    key = ProofKey()
    try:
        device = device_token(key)
        user_token = xbox_user(msa["access_token"])
        xbox, xerr = xsts(user_token, "http://xboxlive.com", device, key)
        if not xbox:
            raise SystemExit("Xbox token failed: %s" % xerr)
        minecraft, mc_err = xsts(user_token, "rp://api.minecraftservices.com/", device, key)
        playfab, pf_err = xsts(user_token, "http://playfab.xboxlive.com/", device, key)
        if not playfab:
            raise SystemExit("PlayFab token failed: %s" % pf_err)
    finally:
        key.close()
    header, claim = auth_header(xbox)
    mc_header = auth_header(minecraft)[0] if minecraft else header
    pf_header = auth_header(playfab)[0]
    exp = jwt_exp(xbox["Token"])
    for doc in (minecraft, playfab):
        got = jwt_exp(doc["Token"]) if doc else 0
        if got:
            exp = min(exp, got) if exp else got
    if not exp:
        exp = int(time.time()) + 4 * 3600
    write_tokens([
        ("exp", str(exp)),
        ("xuid", claim.get("xid", "0")),
        ("uhs", claim.get("uhs", "")),
        ("gamertag", claim.get("gtg", "Player")),
        ("xbox", header),
        ("mc", mc_header),
        ("playfab", pf_header),
        ("msa", msa["access_token"]),
        ("refresh", msa.get("refresh_token", "")),
        ("mc_error", "" if minecraft else str(mc_err or "")),
    ])


def main():
    repair_stored_exp()
    if cached_ok():
        return
    refresh = load_refresh()
    if refresh:
        refreshed = refresh_msa(refresh)
        if refreshed:
            finish(refreshed)
            return
    started = post("https://login.live.com/oauth20_connect.srf", form={
        "client_id": CLIENT,
        "scope": SCOPE,
        "response_type": "device_code",
    })
    if "device_code" not in started:
        raise SystemExit("Could not start Microsoft login: %s" % started.get("error"))
    show_code(started.get("verification_uri") or "https://www.microsoft.com/link", started["user_code"])
    finish(poll_msa(started["device_code"], started.get("interval", 5), started.get("expires_in", 900)))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if exc.code not in (0, None):
            with open(os.path.join(HERE, "login-error.txt"), "w", encoding="utf-8") as handle:
                handle.write(str(exc.code or exc)[:400])
        raise
