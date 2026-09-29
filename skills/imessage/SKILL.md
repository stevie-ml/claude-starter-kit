---
name: imessage
description: This skill should be used when the user asks to "read my iMessages", "find my messages to", "read my texts", "what did I say to", "check my messages with", or mentions reading iMessage conversations by contact name or phone number. Provides the complete method for querying the local iMessage database.
tools: Bash, Read
---

# iMessage Reader

Read iMessages from the local macOS Messages database at `~/Library/Messages/chat.db`.

## Finding a conversation

**Always resolve contact names via osascript first.** The local AddressBook SQLite file is nearly empty (iCloud contacts are not stored there). Use the Contacts app via AppleScript instead:

```bash
osascript -e '
tell application "Contacts"
  set results to {}
  repeat with p in every person
    set fn to first name of p
    set ln to last name of p
    set fullName to ""
    if fn is not missing value then set fullName to fn
    if ln is not missing value then set fullName to fullName & " " & ln
    if fullName contains "NAME" then
      set nums to {}
      repeat with ph in phones of p
        set nums to nums & {value of ph}
      end repeat
      set results to results & {fullName & ": " & (nums as string)}
    end if
  end repeat
  return results
end tell'
```

This returns name + phone number(s). Strip non-digits from the number and use it to query chat.db with LIKE.

If a phone number is given directly, skip the contact lookup and use it as-is.

## Reading messages

Full conversation with timestamps and sender labels:

```sql
sqlite3 ~/Library/Messages/chat.db "
SELECT
  datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
  CASE WHEN m.is_from_me = 1 THEN 'You' ELSE 'Them' END as sender,
  COALESCE(m.text, '[attachment]') as msg
FROM message m
JOIN chat_message_join cmj ON m.rowid = cmj.message_id
JOIN chat c ON cmj.chat_id = c.rowid
WHERE c.chat_identifier LIKE '%IDENTIFIER%'
ORDER BY m.date ASC;"
```

## Handling attributedBody blobs

Some messages have NULL text but contain an `attributedBody` blob (rich text). Extract with Python:

```python
import sqlite3, os

db = os.path.expanduser('~/Library/Messages/chat.db')
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute('''
    SELECT m.rowid, m.text, m.attributedBody,
           datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
           m.is_from_me
    FROM message m
    JOIN chat_message_join cmj ON m.rowid = cmj.message_id
    JOIN chat c ON cmj.chat_id = c.rowid
    WHERE c.chat_identifier LIKE '%IDENTIFIER%'
    ORDER BY m.date ASC
''')

for rowid, text, abody, date, is_from_me in cur.fetchall():
    sender = 'You' if is_from_me else 'Them'
    if text:
        print(f"{date} | {sender} | {text}")
    elif abody:
        # attributedBody is a binary plist; extract the NSString
        try:
            blob = bytes(abody)
            # Find the NSString content between known markers
            idx = blob.find(b'NSString')
            if idx != -1:
                # Skip past the type info to find the actual text
                search_start = idx + 8
                # Look for the length byte and extract
                for i in range(search_start, min(search_start + 50, len(blob))):
                    if blob[i:i+1].isascii() and blob[i] > 31:
                        end = blob.find(b'\x00', i)
                        if end == -1: end = len(blob)
                        decoded = blob[i:end].decode('utf-8', errors='ignore').strip()
                        if len(decoded) > 1:
                            print(f"{date} | {sender} | {decoded}")
                            break
        except:
            print(f"{date} | {sender} | [rich text - could not decode]")

conn.close()
```

## Key facts

- macOS iMessage timestamps: `date/1000000000 + 978307200` converts to unix epoch
- `chat_identifier` is a phone number (e.g. `+16108444495`) or email
- `is_from_me = 1` means sent by user, `0` means received
- Attachments are in `~/Library/Messages/Attachments/`
- The database is unencrypted and readable with standard sqlite3
