Paste everything below the line into Claude Code.

---

Set up my Claude Code with the starter kit at https://github.com/stevie-ml/claude-starter-kit. Work through these steps in order and tell me what you did at the end.

1. **Ask me first**, in one message: my name (for chart attribution), my cell number for iMessage alerts (format +15551234567), a line or two about who I am (school, major, job), and any writing preferences I have. Also confirm whether I'm on a Mac. If I'm not, skip everything marked (Mac).

2. **Clone** the repo to `~/claude-starter-kit` (or `git pull` if it's already there).

3. **Install the skills.** Copy each folder in `skills/` into `~/.claude/skills/`, and each file in `agents/` into `~/.claude/agents/`. If a skill with the same name already exists, show me the difference and ask before overwriting. Then replace the placeholders in the copied files (not the repo): `{{YOUR_NAME}}` with my name, `{{YOUR_PHONE}}` with my number. `chmod +x` every file in a `scripts/` folder. Skip `imessage`, `signal`, `text-me` and the `signal-reader` agent if I'm not on a Mac.

4. **CLAUDE.md.** If `~/.claude/CLAUDE.md` doesn't exist, create it from `templates/CLAUDE.md` with my answers filled in. If it does exist, show me what you'd add and merge only with my OK.

5. **Dependencies.** Install what's missing, checking first:
   - Homebrew (Mac) if it's not there. Ask before installing it.
   - Node.js (needed for Playwright): `brew install node` on Mac.
   - Python packages: `pip3 install --user matplotlib numpy cryptography`
   - (Mac) `brew install sqlcipher` for the Signal skill.

6. **MCP servers.** Add Playwright so you can drive a real browser:
   `claude mcp add playwright --scope user -- npx @playwright/mcp@latest`
   Then run `npx playwright install chromium`.

7. **Anthropic's document skills** (Word, Excel, PowerPoint, PDF, plus skill-creator for making my own skills). Tell me to run these two commands myself inside Claude Code, since slash commands can't be run from here:
   `/plugin marketplace add anthropics/skills`
   `/plugin install document-skills@anthropic-agent-skills`
   `/plugin install example-skills@anthropic-agent-skills` (this one has skill-creator)
   Check `claude plugin --help` first in case the syntax has changed, and give me the right version.

8. **Optional logins.** Ask which of these I want, and walk me through only those, one at a time:
   - **Gmail reading** (the `email` skill): I make an app password at https://myaccount.google.com/apppasswords (needs 2-Step Verification on). Save `~/.claude/skills/email/gmail.conf` with `GMAIL_USER=` and `GMAIL_APP_PASSWORD=` lines, `chmod 600` it, and test with `python3 ~/.claude/skills/email/scripts/gmail.py recent 3`.
   - **Spotify**: I create an app at https://developer.spotify.com/dashboard with redirect URI `http://127.0.0.1:8888/callback`. Save `~/.claude/skills/spotify/spotify.conf` with `SPOTIFY_CLIENT_ID=`, `SPOTIFY_CLIENT_SECRET=`, `SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback`, then run `python3 ~/.claude/skills/spotify/scripts/spotify.py auth`.
   - **Anki**: install Anki from https://apps.ankiweb.net, then Tools → Add-ons → Get Add-ons → code `2055492159` (AnkiConnect), restart Anki. Test with `curl -s localhost:8765 -X POST -d '{"action":"deckNames","version":6}'`.
   - **Google connectors** (Gmail, Calendar, Drive through claude.ai): tell me to turn them on at claude.ai → Settings → Connectors. They show up in Claude Code automatically when I'm logged in with the same account.
   - (Mac) **iMessage / Signal reading**: give Terminal (or VS Code, whichever I'm using) Full Disk Access in System Settings → Privacy & Security → Full Disk Access, then restart it.

9. **Test.** (Mac) Send me a test text with `~/.claude/skills/text-me/scripts/text_me.sh "Claude Code is set up"`. Make a quick test chart with the research-chart skill and open it. Report what works and what still needs me.

Never put my passwords or tokens in the repo folder or anywhere but the config files named above.
