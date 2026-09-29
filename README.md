# Claude Code starter kit

Skills, an agent, and setup steps that make Claude Code more useful day to day.

**To install:** open Claude Code and paste in the contents of [INSTALL_PROMPT.md](INSTALL_PROMPT.md). It asks a few questions, installs everything, and walks you through the optional logins.

## What's in it

| Skill | What it does |
|---|---|
| `text-me` | Claude texts you on iMessage when something breaks or needs you and you've walked away (Mac) |
| `anki` | Turns lecture slides, PDFs and notes into atomic, quiz-style Anki cards and adds them directly |
| `confused` | Say "I don't get X" and it adds 5-8 targeted Anki cards on exactly that |
| `draft-editing` | Edits your drafts with cuts and small inserts instead of rewriting them in its own voice |
| `research-chart` | Clean dark-theme charts for posting, with a check that fails if any labels overlap |
| `tufte-viz` | Picks and critiques chart designs using Tufte's principles |
| `email` | Reads and searches Gmail over IMAP (needs an app password) |
| `imessage` | Reads your iMessage history from the local database (Mac) |
| `signal` + `signal-reader` agent | Decrypts and reads Signal Desktop messages (Mac) |
| `spotify` | Reads what you're playing, top tracks, playlists; controls playback |

Also set up by the install prompt:
- **Playwright MCP**: Claude drives a real Chrome window (logins, forms, scraping, screenshots).
- **Anthropic document skills**: Word, Excel, PowerPoint and PDF files, plus `skill-creator` for writing your own skills.
- **`~/.claude/CLAUDE.md`**: a personal context file Claude reads every session.

## Making your own skills

A skill is a folder in `~/.claude/skills/` with a `SKILL.md`. The `description` line at the top decides when Claude uses it, so write it as "Use this when the user asks...". Easiest route: tell Claude "make me a skill for X" once skill-creator is installed.
