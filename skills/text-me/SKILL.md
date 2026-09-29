---
name: text-me
description: Use this skill to text the user an iMessage when something needs their attention and they may not be watching the terminal. Trigger it when a long task finishes, when a submission, upload or send fails, when a deadline is close and Claude is waiting on an answer, or when the user says "text me when...". Macs only.
tools: Bash
---

# Text Me

The user often walks away from the terminal. A message in the chat that they never see is worthless if a deadline is running. This skill sends them an iMessage instead.

```bash
~/.claude/skills/text-me/scripts/text_me.sh "message"          # send now
~/.claude/skills/text-me/scripts/text_me.sh -d 120 "message"   # send in 2 min unless cancelled
~/.claude/skills/text-me/scripts/text_me.sh -c                 # cancel the queued one
```

Texting the user themself is a notification, not an outward action, so it does not need their permission. Texting anyone else does.

## When to text

**Immediately:**
- A submission, upload, send or post they asked for failed or was rejected
- A deadline is close and you still need an answer from them
- An irreversible action could not complete

**On a 2 minute delay (`-d 120`):** anything important is waiting on them at the end of your turn. If they reply before it fires, cancel it with `-c` first thing. That way they never see it if they were watching, and get pulled back if they wandered off.

Err toward texting. An unneeded text costs two seconds. A missed one can cost an assignment.

## Style

One or two short sentences. Say what happened and what you need. No greeting.

## Troubleshooting

- First run: macOS asks to let the terminal/VS Code control Messages. Click OK. If it was denied, re-enable in System Settings → Privacy & Security → Automation.
- Messages must be signed in to iMessage.
