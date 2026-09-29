---
name: anki
description: This skill should be used when the user asks to "make Anki cards", "create flashcards", "add to Anki", "make cards for", "Anki this", or mentions creating spaced repetition cards from lectures, slides, PDFs, or quizzes. Provides best practices and the technical method for adding cards to Anki.
tools: Bash, Read
---

# Anki Card Creator

Create high-quality Anki flashcards from academic materials and add them directly to Anki via AnkiConnect.

## Card quality rules (MANDATORY — check every card against these before adding)

1. **Atomic**: One fact per card. NEVER combine two questions with "and" / "," / "why" appended.
   - BANNED patterns: "What is X, and what is its formula?", "What is X and why?", "What range must X fall in, and why?"
   - If a card asks "what" AND "why" or "what" AND "formula" → SPLIT into 2 cards.
   - Rule of thumb: if the front has a comma or "and" joining two interrogatives, it MUST be split.
2. **Quiz-style**: Frame as questions that could appear on an exam. Use "What is...", "How do you...", "What happens when...", "Interpret this output:".
3. **Concrete**: Include actual code examples, R output, or data to interpret — not abstract definitions.
4. **Plain language**: Explain what variables actually mean. No unexplained notation.
5. **Include images** when helpful (R plots, regression output screenshots, graphs).
6. **Concise backs**: 1-3 sentences max. No mini-lectures. If more detail is needed, make separate cards.
7. **No Q:/A: prefixes**: Don't put `<strong>Q:</strong>` or `<strong>A:</strong>` in fields — Anki already shows front/back.
8. **Consistent HTML**: Use `<b>` for emphasis, `<code>` for code, `<br>` for breaks. No `<div>`, `<blockquote>`, or inline styles.
9. **Always tag**: Every card must have at least one tag (course code + topic). Never leave tags empty.
10. **No manual reversed pairs**: If a card needs both directions, use model "Basic (and reversed card)" instead of creating two separate notes.

## Front vs back design theory (Wozniak's 20 Rules)

The front determines which retrieval pathway you strengthen. Design accordingly:

**Front = the retrieval cue. Back = the minimum answer.**
- Put the concept/question on the front, the formula/fact on the back — this trains recall (concept → answer), which is what exams test.
- Don't flip it (formula on front, concept on back) unless you specifically want recognition practice.

**Minimum information principle**
Each card = one retrieval pathway. The more packed in, the worse retention gets for all of it. If the back has two distinct facts, split the card.

**Avoid sets and enumerations**
Never ask "list the three X" as one card — unordered lists can't be reliably learned. Instead make one card per item with context:
- BAD: "What are the three approaches to GDP?"
- GOOD: "What does the value-added approach to GDP measure?" (one card per approach)

**Cloze deletion for formulas**
Often better than Q&A for equations. Fill-in-the-blank forces recall of the specific missing piece:
- GOOD cloze: "GDP deflator = (___ / Real GDP) × 100"
- Anki model: "Cloze" with {{c1::Nominal GDP}} syntax

**Use concrete examples, not abstract definitions**
Abstract definitions resist interference. Anchor to a scenario the student has already worked through:
- WEAK: "What is diminishing returns?"
- STRONG: "In the Malthusian model, if a plague kills half the workers, what happens to GDP per capita?"

**Back length**
- Formula cards: just the formula, maybe one clarifying note in parentheses
- Concept cards: 1-2 sentences max
- If you need more than 2 sentences, the card is covering two facts — split it

## Bad vs good cards

**Bad** (two questions in one):
```
Q: What is SSR, and what is its formula?
A: Sum of Squares Regression. SSR = Σ(ŷᵢ − ȳ)²...
```

**Good** (split into two atomic cards):
```
Card 1:
Q: What is SSR (Sum of Squares Regression)?
A: The explained variability — how much of Y's variance is captured by the model's predictions.

Card 2:
Q: What is the formula for SSR?
A: SSR = Σ(ŷᵢ − ȳ)²
```

**Bad** (vague front):
```
Q: what does seq do r
```

**Good** (specific):
```
Q: What does seq(from=1, to=10, by=2) return in R?
A: c(1, 3, 5, 7, 9)
```

## Adding cards via AnkiConnect

AnkiConnect must be running (Anki must be open with AnkiConnect add-on installed).

### Add a single card

```bash
curl -s localhost:8765 -X POST -d '{
  "action": "addNote",
  "version": 6,
  "params": {
    "note": {
      "deckName": "DECK_NAME",
      "modelName": "Basic",
      "fields": {
        "Front": "Question here",
        "Back": "Answer here"
      },
      "options": {
        "allowDuplicate": false
      },
      "tags": ["TAG"]
    }
  }
}'
```

### Add multiple cards at once

```python
import json, subprocess

cards = [
    {"front": "Q1", "back": "A1"},
    {"front": "Q2", "back": "A2"},
]

deck = "DECK_NAME"
tag = "course topic"

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
                "tags": [tag]
            }
        }
    }
    result = subprocess.run(
        ['curl', '-s', 'localhost:8765', '-X', 'POST', '-d', json.dumps(payload)],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    if resp.get('error'):
        print(f"Error: {resp['error']}")
    else:
        print(f"Added: {card['front'][:50]}...")
```

### Check existing decks

```bash
curl -s localhost:8765 -X POST -d '{"action": "deckNames", "version": 6}'
```

### Add card with image

```bash
curl -s localhost:8765 -X POST -d '{
  "action": "addNote",
  "version": 6,
  "params": {
    "note": {
      "deckName": "DECK",
      "modelName": "Basic",
      "fields": {
        "Front": "What does this R output tell you?<br><img src=\"output.png\">",
        "Back": "Answer here"
      },
      "picture": [{
        "path": "/absolute/path/to/output.png",
        "filename": "output.png",
        "fields": ["Front"]
      }]
    }
  }
}'
```

## Workflow

1. Read the source material (PDF, PPTX, quiz, R code)
2. Identify the key concepts and exam-likely questions
3. Draft atomic cards with concrete examples
4. Add to Anki via AnkiConnect

## Decks

Check existing decks with `deckNames` before adding. Ask which deck if it is not obvious from context.

## Key facts

- AnkiConnect runs on localhost:8765
- Anki must be open for AnkiConnect to work
- Use "Basic" model for simple Q&A, "Basic (and reversed card)" for bidirectional
- HTML is supported in fields (use `<br>` for line breaks, `<code>` for inline code)
- Tags help organize by lecture/topic
- No need to present cards for review — just add them directly
