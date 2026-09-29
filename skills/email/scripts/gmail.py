#!/usr/bin/env python3
"""
Direct Gmail IMAP reader. Bypasses Mail.app entirely.
Usage:
  gmail.py recent [N]                  - show N most recent inbox messages (default 10)
  gmail.py search sender <name>        - search by sender name or address
  gmail.py search subject <keyword>    - search by subject keyword
  gmail.py search today                - messages received today
  gmail.py read <uid>                  - read full body of a message by UID
"""

import imaplib
import email
from email.header import decode_header
import sys
import os
import datetime

CONF = os.path.expanduser("~/.claude/skills/email/gmail.conf")

def load_creds():
    creds = {}
    with open(CONF) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    return creds["GMAIL_USER"], creds["GMAIL_APP_PASSWORD"]

def connect():
    user, password = load_creds()
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(user, password)
    return mail

def decode_str(s):
    if s is None:
        return ""
    parts = decode_header(s)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)

def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                return part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
        # fallback to html if no plain text
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                import html as htmlmod
                raw = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
                # strip tags crudely
                import re
                text = re.sub(r"<[^>]+>", " ", raw)
                text = re.sub(r"[ \t]+", " ", text)
                text = re.sub(r"\n{3,}", "\n\n", text)
                return htmlmod.unescape(text).strip()
    else:
        return msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="replace"
        )
    return ""

def format_message(uid, msg, include_body=False, body_limit=6000):
    subject = decode_str(msg["Subject"])
    sender = decode_str(msg["From"])
    date = msg["Date"]
    out = f"UID: {uid}\nFrom: {sender}\nSubject: {subject}\nDate: {date}\n"
    if include_body:
        body = get_body(msg)
        if len(body) > body_limit:
            body = body[:body_limit] + f"\n\n[truncated at {body_limit} chars]"
        out += f"---\n{body}\n"
    return out

def cmd_recent(mail, n=10):
    mail.select("INBOX")
    _, data = mail.search(None, "ALL")
    uids = data[0].split()
    uids = uids[-n:][::-1]  # most recent N, newest first
    results = []
    for uid in uids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        results.append(format_message(uid.decode(), msg))
    return "\n".join(results)

def cmd_search_sender(mail, name):
    mail.select("INBOX")
    _, data = mail.search(None, f'FROM "{name}"')
    uids = data[0].split()[-20:][::-1]
    if not uids:
        return f"No messages from '{name}' found."
    results = []
    for uid in uids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        results.append(format_message(uid.decode(), msg))
    return "\n".join(results)

def cmd_search_subject(mail, keyword):
    mail.select("INBOX")
    _, data = mail.search(None, f'SUBJECT "{keyword}"')
    uids = data[0].split()[-20:][::-1]
    if not uids:
        return f"No messages with subject containing '{keyword}' found."
    results = []
    for uid in uids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        results.append(format_message(uid.decode(), msg))
    return "\n".join(results)

def cmd_search_today(mail):
    today = datetime.date.today().strftime("%d-%b-%Y")
    mail.select("INBOX")
    _, data = mail.search(None, f'SINCE "{today}"')
    uids = data[0].split()[::-1]
    if not uids:
        return "No messages received today."
    results = []
    for uid in uids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        results.append(format_message(uid.decode(), msg))
    return "\n".join(results)

def cmd_read(mail, uid):
    mail.select("INBOX")
    _, msg_data = mail.fetch(uid.encode(), "(RFC822)")
    if not msg_data or msg_data[0] is None:
        return f"Message UID {uid} not found."
    msg = email.message_from_bytes(msg_data[0][1])
    return format_message(uid, msg, include_body=True)

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    mail = connect()

    try:
        cmd = args[0]
        if cmd == "recent":
            n = int(args[1]) if len(args) > 1 else 10
            print(cmd_recent(mail, n))
        elif cmd == "search":
            if len(args) < 3:
                print("Usage: gmail.py search sender|subject|today <value>")
                sys.exit(1)
            kind = args[1]
            if kind == "sender":
                print(cmd_search_sender(mail, args[2]))
            elif kind == "subject":
                print(cmd_search_subject(mail, args[2]))
            elif kind == "today":
                print(cmd_search_today(mail))
            else:
                print(f"Unknown search type: {kind}")
        elif cmd == "read":
            print(cmd_read(mail, args[1]))
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    finally:
        mail.logout()

if __name__ == "__main__":
    main()
