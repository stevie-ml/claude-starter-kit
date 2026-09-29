---
name: confused
description: Use this skill when the user says they don't get something, are confused, or asks for help understanding a concept mid-conversation. Look at what they're stuck on from context, then immediately generate and add targeted Anki cards drilling that specific concept from multiple angles. No confirmation needed — just make the cards and add them.
tools: Bash
---

# Confused → Anki Cards

When the user is confused about something, do this:

1. **Identify the concept** from conversation context — what exactly are they stuck on?
2. **Generate 5–8 atomic cards** targeting that specific sticking point from multiple angles:
   - The core definition / what it is
   - The formula or procedure (if any)
   - Why it works / intuition
   - A concrete real-world example
   - A common mistake or misconception
   - A quiz-style application question (plug-in-numbers or interpret-output style)
3. **Add to Anki immediately** via AnkiConnect — no confirmation needed
4. **Tell the user** how many cards were added and what angles they cover

## Card quality rules (same as anki skill)

- Atomic: one fact per card, no "and" joining two questions
- Quiz-style fronts: "What is...", "What happens when...", "Interpret this..."
- Concrete: use actual numbers, formulas, examples — not abstract definitions
- Back: 1–3 sentences max
- Tags: always tag with course + topic (e.g. "stats regression")
- No Q:/A: prefixes

## Deck and tags

- Deck: the deck for that course or subject (check `deckNames`; ask once if unclear)
- Tag format: "<course> <topic>", e.g. "bio cellresp", "stats regression"

## Adding cards via AnkiConnect

```python
import json, subprocess

def add_cards(cards, deck="DECK_NAME", tag="TAG"):
    results = []
    for card in cards:
        payload = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck,
                    "modelName": "Basic",
                    "fields": {
                        "Front": card["front"],
                        "Back": card["back"]
                    },
                    "options": {"allowDuplicate": False},
                    "tags": card.get("tags", [tag])
                }
            }
        }
        result = subprocess.run(
            ['curl', '-s', 'localhost:8765', '-X', 'POST', '-d', json.dumps(payload)],
            capture_output=True, text=True
        )
        resp = json.loads(result.stdout)
        results.append((card["front"][:60], resp.get("error")))
    return results
```

## What "multiple angles" means

For any concept X, cover:
- **What**: What is X? (definition card)
- **Formula/procedure**: What is the formula for X? / How do you compute X?
- **Why**: Why does X work this way? What's the intuition?
- **Example**: Give a concrete real-world scenario where X applies
- **Misconception**: What do people wrongly think about X?
- **Application**: Given [numbers/output], what is X? (plug-and-chug or interpret)
- **Comparison**: How does X differ from Y? (if a related concept exists)

Don't mechanically make all 7 — pick the angles that address what the user was actually confused about.
