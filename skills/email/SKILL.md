---
name: email
description: Use this skill when the user asks to "read my email", "check my inbox", "find emails from", "show me emails about", "read that email", "any emails from X", "what did X email me", or any request to access, search, or summarize email content.
tools: Bash
---

# Email Reader

Reads email directly from Gmail via IMAP using the script at `~/.claude/skills/email/scripts/gmail.py`.
Credentials (Gmail address + app password) in `~/.claude/skills/email/gmail.conf`.

Do NOT use AppleScript or Mail.app — it is stuck and not synced.

## Show today's emails

```bash
python3 ~/.claude/skills/email/scripts/gmail.py search today x
```

## Show N most recent inbox messages

```bash
python3 ~/.claude/skills/email/scripts/gmail.py recent 10
```

## Search by sender name or address

```bash
python3 ~/.claude/skills/email/scripts/gmail.py search sender "Matt Levine"
```

## Search by subject keyword

```bash
python3 ~/.claude/skills/email/scripts/gmail.py search subject "Money Stuff"
```

## Read full body of a message (by UID from search results)

```bash
python3 ~/.claude/skills/email/scripts/gmail.py read <UID>
```

## Workflow for "read email from X today"

1. Run `search today x` to list today's messages and find the UID
2. Run `read <UID>` to get the full body
3. Summarize the content for the user

## Key facts

- UIDs are stable identifiers shown in all search results
- Body is plain text extracted from HTML; truncated at 6000 chars by default
- `search today` uses IMAP SINCE, always live from Gmail's servers
- Credentials file: `~/.claude/skills/email/gmail.conf`
