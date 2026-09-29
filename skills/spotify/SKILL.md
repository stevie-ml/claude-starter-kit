---
name: spotify
description: Use this skill when the user asks to "what am I listening to", "what's playing on Spotify", "check my Spotify", "show my top artists/tracks", "my recently played", "my playlists", "play something on Spotify", "pause Spotify", "skip this song", "search Spotify", or any request to read or control their Spotify account.
tools: Bash
---

# Spotify

Reads and controls the user's Spotify via the Web API using the zero-dependency
script at `~/.claude/skills/spotify/scripts/spotify.py` (stdlib only, no
pip installs). Credentials live in
`~/.claude/skills/spotify/spotify.conf`.

Auth uses the OAuth Authorization Code flow: a one-time browser login mints a
refresh token, after which every command silently gets a fresh access token.

## First-time setup (once)

1. In the Spotify Developer Dashboard for the app, add this Redirect URI:
   `http://127.0.0.1:8888/callback` (Spotify requires the loopback IP, not
   `localhost`). Save.
2. Run the auth flow — this opens a browser, the user approves, done:

   ```bash
   python3 ~/.claude/skills/spotify/scripts/spotify.py auth
   ```

   The refresh token is saved to `spotify.conf`. No need to repeat unless the
   token is revoked.

## Reading

```bash
# Currently playing
python3 ~/.claude/skills/spotify/scripts/spotify.py now

# Recently played (default 20)
python3 ~/.claude/skills/spotify/scripts/spotify.py recent 30

# Top tracks or artists. time range: short_term (~4wk), medium_term (~6mo), long_term (~years)
python3 ~/.claude/skills/spotify/scripts/spotify.py top tracks 20 short_term
python3 ~/.claude/skills/spotify/scripts/spotify.py top artists 20 long_term

# Playlists, then tracks in one
python3 ~/.claude/skills/spotify/scripts/spotify.py playlists
python3 ~/.claude/skills/spotify/scripts/spotify.py playlist <playlist_id> 100

# Account info
python3 ~/.claude/skills/spotify/scripts/spotify.py me

# Search: type = track | artist | album | playlist
python3 ~/.claude/skills/spotify/scripts/spotify.py search track bad guy billie eilish
```

## Playback control

Requires an active device (Spotify open somewhere). Check devices first if
"play" errors with "no active device".

```bash
python3 ~/.claude/skills/spotify/scripts/spotify.py devices
python3 ~/.claude/skills/spotify/scripts/spotify.py play              # resume
python3 ~/.claude/skills/spotify/scripts/spotify.py play spotify:track:XXXX
python3 ~/.claude/skills/spotify/scripts/spotify.py play spotify:playlist:XXXX
python3 ~/.claude/skills/spotify/scripts/spotify.py pause
python3 ~/.claude/skills/spotify/scripts/spotify.py next
python3 ~/.claude/skills/spotify/scripts/spotify.py prev
```

## Escape hatch

Any Web API endpoint not wrapped above:

```bash
python3 ~/.claude/skills/spotify/scripts/spotify.py raw GET /me/tracks?limit=10
```

## Notes

- Scopes cover reading library/playback/top/recent + playback control +
  playlist read/modify. If a call 403s on scope, re-run `auth` (the scope list
  is at the top of the script).
- Spotify may rotate the refresh token; the script auto-persists a new one.
