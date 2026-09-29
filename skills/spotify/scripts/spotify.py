#!/usr/bin/env python3
"""Spotify Web API client. Zero external dependencies (stdlib only).

Config lives in ~/.claude/skills/spotify/spotify.conf
Auth uses the OAuth Authorization Code flow. Run `auth` once to get a refresh
token; after that every command silently mints a fresh access token.
"""
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

CONF_PATH = os.path.expanduser(
    "~/.claude/skills/spotify/spotify.conf"
)

# Scopes: enough for reading library/playback and controlling playback.
SCOPES = " ".join([
    "user-read-private",
    "user-read-email",
    "user-read-currently-playing",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-recently-played",
    "user-top-read",
    "user-library-read",
    "user-library-modify",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-follow-read",
])

API = "https://api.spotify.com/v1"


def load_conf():
    conf = {}
    with open(CONF_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            conf[k.strip()] = v.strip()
    return conf


def save_conf(conf):
    lines = [f"{k}={v}" for k, v in conf.items()]
    with open(CONF_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(CONF_PATH, 0o600)


def basic_auth_header(conf):
    raw = f"{conf['SPOTIFY_CLIENT_ID']}:{conf['SPOTIFY_CLIENT_SECRET']}"
    return "Basic " + base64.b64encode(raw.encode()).decode()


def token_request(conf, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=body,
        headers={
            "Authorization": basic_auth_header(conf),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------- auth (once)
def cmd_auth(conf, args):
    """One-time browser login to obtain a refresh token."""
    redirect = conf["SPOTIFY_REDIRECT_URI"]
    parsed = urllib.parse.urlparse(redirect)
    host, port = parsed.hostname, parsed.port or 8888

    params = urllib.parse.urlencode({
        "client_id": conf["SPOTIFY_CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": redirect,
        "scope": SCOPES,
        "show_dialog": "true",
    })
    auth_url = "https://accounts.spotify.com/authorize?" + params

    holder = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.urlparse(self.path).query
            qs = urllib.parse.parse_qs(q)
            holder["code"] = qs.get("code", [None])[0]
            holder["error"] = qs.get("error", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            msg = ("Auth failed: " + holder["error"]) if holder.get("error") \
                else "Spotify authorized. You can close this tab."
            self.wfile.write(f"<html><body><h2>{msg}</h2></body></html>".encode())

        def log_message(self, *a):
            pass

    server = HTTPServer((host, port), Handler)
    print("Opening browser for Spotify authorization...", file=sys.stderr)
    print("If it doesn't open, visit:\n" + auth_url, file=sys.stderr)
    webbrowser.open(auth_url)
    server.handle_request()  # blocks until the redirect hits
    server.server_close()

    if holder.get("error") or not holder.get("code"):
        print("Authorization failed: " + str(holder.get("error")), file=sys.stderr)
        sys.exit(1)

    tok = token_request(conf, {
        "grant_type": "authorization_code",
        "code": holder["code"],
        "redirect_uri": redirect,
    })
    conf["SPOTIFY_REFRESH_TOKEN"] = tok["refresh_token"]
    save_conf(conf)
    print("Success. Refresh token saved to config.")


def get_access_token(conf):
    if not conf.get("SPOTIFY_REFRESH_TOKEN"):
        print("No refresh token. Run: spotify.py auth", file=sys.stderr)
        sys.exit(1)
    tok = token_request(conf, {
        "grant_type": "refresh_token",
        "refresh_token": conf["SPOTIFY_REFRESH_TOKEN"],
    })
    # Spotify may rotate the refresh token; persist if so.
    if tok.get("refresh_token"):
        conf["SPOTIFY_REFRESH_TOKEN"] = tok["refresh_token"]
        save_conf(conf)
    return tok["access_token"]


def api(access, method, path, params=None, body=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + access)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f"HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)


# ------------------------------------------------------------------ commands
def artists_str(item):
    return ", ".join(a["name"] for a in item.get("artists", []))


def cmd_me(access, args):
    me = api(access, "GET", "/me")
    print(json.dumps({
        "name": me.get("display_name"),
        "id": me.get("id"),
        "email": me.get("email"),
        "product": me.get("product"),
        "followers": me.get("followers", {}).get("total"),
    }, indent=2))


def cmd_now(access, args):
    data = api(access, "GET", "/me/player/currently-playing")
    if not data or not data.get("item"):
        print("Nothing playing.")
        return
    it = data["item"]
    state = "playing" if data.get("is_playing") else "paused"
    print(f"[{state}] {it['name']} — {artists_str(it)}")
    print(f"  album: {it.get('album', {}).get('name')}")
    print(f"  url:   {it.get('external_urls', {}).get('spotify')}")


def cmd_recent(access, args):
    n = int(args[0]) if args else 20
    data = api(access, "GET", "/me/player/recently-played", {"limit": n})
    for i, entry in enumerate(data.get("items", []), 1):
        t = entry["track"]
        print(f"{i:>2}. {t['name']} — {artists_str(t)}")


def cmd_top(access, args):
    kind = args[0] if args else "tracks"  # tracks | artists
    n = int(args[1]) if len(args) > 1 else 20
    time_range = args[2] if len(args) > 2 else "medium_term"
    data = api(access, "GET", f"/me/top/{kind}",
               {"limit": n, "time_range": time_range})
    for i, item in enumerate(data.get("items", []), 1):
        if kind == "artists":
            print(f"{i:>2}. {item['name']}  ({', '.join(item.get('genres', [])[:3])})")
        else:
            print(f"{i:>2}. {item['name']} — {artists_str(item)}")


def cmd_playlists(access, args):
    n = int(args[0]) if args else 50
    data = api(access, "GET", "/me/playlists", {"limit": n})
    for pl in data.get("items", []):
        print(f"{pl['name']}  ({pl['tracks']['total']} tracks)  [{pl['id']}]")


def cmd_playlist(access, args):
    """Show tracks in a playlist by id."""
    pid = args[0]
    n = int(args[1]) if len(args) > 1 else 100
    data = api(access, "GET", f"/playlists/{pid}/tracks", {"limit": n})
    for i, entry in enumerate(data.get("items", []), 1):
        t = entry.get("track") or {}
        print(f"{i:>3}. {t.get('name')} — {artists_str(t)}")


def cmd_search(access, args):
    """search <type> <query...>  type = track|artist|album|playlist"""
    typ = args[0]
    q = " ".join(args[1:])
    data = api(access, "GET", "/search", {"q": q, "type": typ, "limit": 15})
    items = data.get(typ + "s", {}).get("items", [])
    for it in items:
        if typ == "track":
            print(f"{it['name']} — {artists_str(it)}  [{it['uri']}]")
        elif typ == "artist":
            print(f"{it['name']}  [{it['uri']}]")
        elif typ == "album":
            print(f"{it['name']} — {artists_str(it)}  [{it['uri']}]")
        else:
            print(f"{it['name']}  [{it['uri']}]")


def cmd_play(access, args):
    """play [uri]  — resume, or start a track/album/playlist uri."""
    if args:
        uri = args[0]
        if uri.startswith("spotify:track:"):
            body = {"uris": [uri]}
        else:
            body = {"context_uri": uri}
        api(access, "PUT", "/me/player/play", body=body)
    else:
        api(access, "PUT", "/me/player/play")
    print("Playing.")


def cmd_pause(access, args):
    api(access, "PUT", "/me/player/pause")
    print("Paused.")


def cmd_next(access, args):
    api(access, "POST", "/me/player/next")
    print("Skipped.")


def cmd_prev(access, args):
    api(access, "POST", "/me/player/previous")
    print("Back.")


def cmd_devices(access, args):
    data = api(access, "GET", "/me/player/devices")
    for d in data.get("devices", []):
        active = "* " if d.get("is_active") else "  "
        print(f"{active}{d['name']} ({d['type']})  [{d['id']}]")


def cmd_raw(access, args):
    """raw GET|POST|PUT <path>  — escape hatch for any endpoint."""
    method = args[0].upper()
    path = args[1]
    print(json.dumps(api(access, method, path), indent=2))


COMMANDS = {
    "me": cmd_me,
    "now": cmd_now,
    "recent": cmd_recent,
    "top": cmd_top,
    "playlists": cmd_playlists,
    "playlist": cmd_playlist,
    "search": cmd_search,
    "play": cmd_play,
    "pause": cmd_pause,
    "next": cmd_next,
    "prev": cmd_prev,
    "devices": cmd_devices,
    "raw": cmd_raw,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: spotify.py <command> [args]\n"
              "Commands: auth, me, now, recent [n], top [tracks|artists] [n] [short_term|medium_term|long_term],\n"
              "          playlists [n], playlist <id> [n], search <type> <query>,\n"
              "          play [uri], pause, next, prev, devices, raw <METHOD> <path>",
              file=sys.stderr)
        sys.exit(1)

    conf = load_conf()
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "auth":
        cmd_auth(conf, args)
        return

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)

    access = get_access_token(conf)
    COMMANDS[cmd](access, args)


if __name__ == "__main__":
    main()
