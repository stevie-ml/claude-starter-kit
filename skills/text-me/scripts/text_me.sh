#!/bin/bash
# Text the user over iMessage. Usage:
#   text_me.sh "message"              -> send now
#   text_me.sh -d 120 "message"       -> send in 120s unless cancelled
#   text_me.sh -c                     -> cancel a pending delayed text
NUM="{{YOUR_PHONE}}"
FLAG="/tmp/.claude_text_me_pending"

if [ "$1" = "-c" ]; then rm -f "$FLAG"; echo "cancelled"; exit 0; fi

DELAY=0
if [ "$1" = "-d" ]; then DELAY="$2"; shift 2; fi
MSG="$1"

send() {
  osascript - "$NUM" "$MSG" <<'APPLESCRIPT'
on run argv
  tell application "Messages"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant (item 1 of argv) of targetService
    send (item 2 of argv) to targetBuddy
  end tell
end run
APPLESCRIPT
}

if [ "$DELAY" -gt 0 ]; then
  touch "$FLAG"
  ( sleep "$DELAY"; [ -f "$FLAG" ] && { send; rm -f "$FLAG"; } ) &
  echo "queued in ${DELAY}s (cancel with -c)"
else
  send && echo sent
fi
