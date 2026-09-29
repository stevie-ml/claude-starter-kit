---
name: research-chart
description: Create a polished, dark-themed research chart optimized for Twitter/X posting, with attribution to {{YOUR_NAME}}. Use when the user asks to make a chart, graph, or visualization from data.
tools: Bash, Read, Write
---

# Research Chart Skill

Create a dark-themed matplotlib chart optimized for Twitter/X (1200×675px or square 1080×1080px), attributed to {{YOUR_NAME}}.


## Titles must be bland and descriptive, never editorial

The title states **what is plotted**, plainly. It is not a headline, an argument, or a punchline. Write the title the way you'd label a figure in a journal: the metric, the population, and the time span.

- Good: "US median household income by state, 2023"
- Good: "Share of SAT submitters scoring 1500+, by application year"
- Bad: "A 1560 Isn't What It Used to Be", "The Arms Race Slammed Into the Ceiling", "The SAT's Blind Spot Swallowed the Pool"

Rule of thumb: the neutral, descriptive sentence that would otherwise be the **subtitle is the title**. If a chart needs a subtitle at all, it carries a secondary clarifier (definitions, scope, caveat), not a thesis. Let the reader draw the conclusion; the chart's job is to show the data, not announce the take. Never editorialize, never use a rhetorical or clever title for a research chart.

## ⚠️ READABILITY IS RULE ZERO — overlapping text is a hard failure

The most common defect in these charts is text that overlaps and becomes unreadable. That is now PREVENTED MECHANICALLY, not eyeballed. **Always build charts with the helper module** `sm_chart.py` in this skill directory. Its `finalize()` measures the pixel bounding box of every text element and **raises `AssertionError` if any two collide** — so a chart with overlapping text cannot be saved. Never hand-roll a chart that skips this check.

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
from sm_chart import new_fig, smart_xticks, hbar, label_points, finalize, BG, PANEL, GRID, TEXT, MUTED, COLORS
```

What the module gives you (all anti-overlap):
- `new_fig(figsize, footer)` — themed fig/ax with **constrained_layout ON** (matplotlib auto-spaces everything) and a reserved bottom strip so the footer never sits on the plot.
- `smart_xticks(ax, labels)` — auto-rotates/wraps x labels so they don't collide. **If you have >7 categories or long labels, use `hbar()` instead** — horizontal bars never overlap their labels.
- `hbar(ax, labels, values)` — horizontal bar chart with value labels placed past each bar end. This is the DEFAULT for "compare a metric across named categories."
- `label_points(ax, xs, ys, texts)` — scatter/line point labels with `adjustText` collision avoidance (installed).
- `finalize(fig, path, source=...)` — adds source + attribution, enforces no-overlap, saves at dpi=200, opens the file. Prints `CLEAN` or raises.

If `finalize` raises, FIX the layout (switch to `hbar`, shorten/wrap labels, raise `figsize`, thin tick density with `MaxNLocator`, move the legend out with `bbox_to_anchor=(1.02,1)`), then re-run. Do not set `strict=False` to silence it unless the user explicitly accepts a minor touch.

Font is Helvetica Neue (falls back to Helvetica/Avenir/Arial). Do NOT also pass `bbox_inches='tight'` — constrained_layout already handles spacing and the two can fight.

## Style Defaults

```python
BG    = '#0f0f0f'   # figure background
PANEL = '#1a1a1a'   # axes background
GRID  = '#2a2a2a'   # gridlines
TEXT  = '#ffffff'   # titles and value labels — use pure white, NOT gray
LABEL = '#ffffff'   # axis labels, tick labels, bar annotations — white for readability
MUTED = '#888888'   # secondary text (footnotes, source lines)
ATTR  = '#666666'   # attribution line
```

**Label color rule**: value labels, axis tick labels, and bar annotations must be `#ffffff`. Gray (`#cccccc` or dimmer) makes them hard to read on dark backgrounds. Only footnotes and attribution use muted colors.

Accent palette — Claude orange first, use in order:
```python
COLORS = ['#D97757', '#69a7df', '#7dbf52', '#ffc933', '#c678dd', '#a9d18e', '#e06c75']
# Claude orange (DEFAULT for single-series charts), steel blue, sage green, gold,
# purple, light green, red — colorblind-friendly, reads well on dark backgrounds
```

## Required Elements

1. **Figure size**: 13×7 for landscape (Twitter banner style), or 10×10 for square
2. **Dark background**: set on both `fig` and `ax`
3. **Frame lines**: hide top/right spines; keep the LEFT and BOTTOM spines visible as axis frames at `#5a5a5a`, linewidth 1.2, with short tick marks (length 4, width 1, color `#5a5a5a`). `new_fig()` sets this up via `style_axes()` automatically.
4. **Horizontal grid only**, color `GRID`, `zorder=0`
5. **Attribution**: bottom-right corner, italic, color `ATTR`:
   ```python
   fig.text(0.98, 0.015, '{{YOUR_NAME}}', ha='right', va='bottom',
            color='#555555', fontsize=10, style='italic')
   ```
6. **Data source line** (if applicable): bottom-left, same style
7. **Value labels** on bars: color `#ffffff` (white, not gray), bold, fontsize 8.5–10
8. **Error bars / confidence intervals**: include whenever the data supports it (mean ± SE, 95% CI, etc.). Use `ax.errorbar(..., fmt='none', color='#ffffff', elinewidth=1.5, capsize=4)`. Never omit them silently — if CIs can't be computed, note why.
9. **Text never overlaps** — enforced by `finalize()` (see Rule Zero above). It raises if any two text elements collide. When it does, the fastest fixes: switch a crowded category chart to `hbar()`; wrap/rotate long labels (`smart_xticks` does this); raise `figsize`; thin ticks with `ax.xaxis.set_major_locator(MaxNLocator(8))`; move the legend out with `loc='upper left', bbox_to_anchor=(1.02, 1)`.
10. **Save via `finalize()`** (dpi=200, `facecolor=BG`, no `bbox_inches='tight'`). It also adds source + attribution and opens the file.

## Chart Archive — MANDATORY

Every chart must be saved as a named source file in `~/charts/`. This allows future conversations to find, tweak, and rebuild any chart without starting over.

Rules:
- Name descriptively: `<topic>_<chart_type>.py` (e.g. `income_by_state_bar.py`)
- The file must be a **standalone runnable script** that regenerates the chart
- Write it to `~/charts/` **before running it**, not after
- When modifying an existing chart, **always `ls ~/charts/` and read the source first** — never rewrite from scratch

## Workflow

1. Understand what data the user wants to visualize
2. Determine chart type (bar, grouped bar, scatter, line, etc.)
3. Ask for the data if not provided, or pull it from context
4. **Write the script to `~/charts/<descriptive_name>.py`** (see Chart Archive above)
5. Run it and open the output
6. Offer to tweak colors, layout, or labels

## Template: Category comparison (DEFAULT — use horizontal bars)

For "compare a metric across named categories," horizontal bars are the safe default: labels never overlap, no matter how long.

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
from sm_chart import new_fig, hbar, finalize, COLORS

labels = [...]   # category names (can be long)
values = [...]   # one number per category

fig, ax = new_fig(figsize=(12, 7))
hbar(ax, labels, values, color=COLORS[0], fmt="{:,.0f}")  # sorts + labels bar ends
ax.set_title("Title Here", fontsize=18, fontweight="bold", pad=14)
ax.set_xlabel("Metric", fontsize=12)
finalize(fig, "~/charts/<name>.png", source="...")
```

## Template: Grouped / vertical bars (few short categories)

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
import numpy as np
from sm_chart import new_fig, smart_xticks, finalize, TEXT, COLORS

groups = [...]              # x-axis category labels
series = {...}             # {'Series name': [values...], ...}
x = np.arange(len(groups)); w = 0.8 / len(series)

fig, ax = new_fig(figsize=(12, 7))
for i, (label, vals) in enumerate(series.items()):
    off = (i - len(series)/2 + 0.5) * w
    ax.bar(x + off, vals, w, color=COLORS[i], label=label, zorder=3)
    for xi, v in zip(x + off, vals):
        if v > 0:
            ax.text(xi, v + max(vals)*0.01, f"{v:,.0f}", ha="center", va="bottom",
                    fontsize=9, color=TEXT, fontweight="bold")   # white, not gray
smart_xticks(ax, groups)   # auto rotate/wrap so labels don't collide
ax.set_ylabel("...", fontsize=12)
ax.set_title("...", fontsize=18, fontweight="bold", pad=14)
ax.legend(frameon=False, labelcolor=TEXT, fontsize=11, loc="upper left",
          bbox_to_anchor=(1.02, 1))    # legend OUTSIDE the plot — never on the data
finalize(fig, "~/charts/<name>.png", source="...")
```

## Template: Scatter / line with point labels

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
from sm_chart import new_fig, label_points, finalize, COLORS
fig, ax = new_fig(figsize=(12, 7))
ax.scatter(xs, ys, color=COLORS[0], s=40, zorder=3)
label_points(ax, xs, ys, names)   # adjustText spreads labels so they don't collide
ax.set_title("...", fontsize=18, fontweight="bold", pad=14)
finalize(fig, "~/charts/<name>.png", source="...")
```


## Template: Two-bar comparison with annotation arrow (e.g. "X under-represented")

Use `paired_value_bars` for the bars + label tiers, `callout_arrow` for the curved arrow.
Both labels in each pair sit at the SAME offset above their bar, so a 8% bar and a
0.2% bar look symmetric instead of one having labels jammed against the top.

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
from sm_chart import new_fig, finalize, paired_value_bars, callout_arrow, TEXT

# data
big = ('8.0%', '0.2%')           # big labels above bar
small = ('347 of 4,347', '2 of 1,087')   # small labels above big
vals = [8.0, 0.18]
colors = ['#5fa6e0', '#d36569']

fig, ax = new_fig(figsize=(13, 9))
ax.set_xlim(-0.6, 1.6); ax.set_ylim(0, 10.4)
paired_value_bars(ax, [0, 1], vals, big_labels=big, small_labels=small,
                  colors=colors, width=0.40)
callout_arrow(ax, (0.17, vals[0] - 1.5), (0.86, vals[1] + 0.95),
              label='43× under-represented', label_xy=(0.55, 4.8))
ax.set_xticks([0, 1])
ax.set_xticklabels(['Share of the\ngraduating class', 'Share of the\ntop quarter'],
                   color=TEXT, fontsize=15)
ax.tick_params(axis='x', pad=14)
ax.set_title('Black students: 1 in 13 of the class, 1 in 500 of the top quarter',
             fontsize=20, fontweight='bold', pad=32, loc='left')
finalize(fig, "~/charts/<name>.png")
```

## Template: Year-by-year stacked bar with segment counts + totals

Use `stacked_bar_with_totals`. Segments with value < 2 are unlabeled (avoids
clutter for tiny slivers); each total sits in white above its column.

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
import numpy as np
from sm_chart import new_fig, finalize, stacked_bar_with_totals, TEXT

years = [2007, 2008, 2009, 2010]
segments = [
    [1, 1, 0, 0],     # top quarter
    [1, 4, 2, 1],     # 2nd
    [7, 10, 6, 2],    # 3rd
    [21, 22, 24, 35], # bottom
]
labels = ['Top', '2nd', '3rd', 'Bottom']
colors = ['#5fb56a', '#5fa6e0', '#ecbb3a', '#d36569']

fig, ax = new_fig(figsize=(14, 8))
x = np.arange(len(years))
totals = stacked_bar_with_totals(ax, x, segments, colors, labels=labels)
ax.set_xticks(x); ax.set_xticklabels([str(y) for y in years], color=TEXT)
ax.set_ylim(0, max(totals) * 1.12)
ax.legend(loc='upper left', frameon=False, labelcolor=TEXT)
finalize(fig, "~/charts/<name>.png")
```

## Template: Grouped bars with Wilson/CI whiskers (3+ groups across categories)

Use `grouped_bars_with_ci` — handles whiskers, value labels above CI whiskers,
and legend in one call.

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
from sm_chart import new_fig, finalize, grouped_bars_with_ci, COLORS, TEXT

cats = ['Strings', 'Piano', 'Percussion']
cis_vals  = [28.9, 25.0, 4.6]
cis_los   = [27.9, 24.1, 4.2]
cis_his   = [29.9, 25.9, 5.1]
trans_vals = [0.0, 18.2, 45.5]
trans_los  = [0.0, 5.1, 21.3]
trans_his  = [25.9, 47.7, 72.0]

fig, ax = new_fig(figsize=(14, 8))
grouped_bars_with_ci(ax, [0, 1, 2],
                    [cis_vals, trans_vals], [cis_los, trans_los], [cis_his, trans_his],
                    colors=[COLORS[1], COLORS[0]],
                    group_labels=['Cis women', 'Trans women'])
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(cats, color=TEXT)
ax.legend(loc='upper right', frameon=False, labelcolor=TEXT)
finalize(fig, "~/charts/<name>.png")
```

## Template: Labeled scatter (countries / states / entities with OLS + r²)

Use `labeled_scatter` for the country-scatter pattern. It handles the four pain
points that kept coming up: no white rim on points, auto-placed labels via
adjustText, optional bubble sizing, and an OLS line + stats box in one call.

```python
import sys; import os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/research-chart"))
from sm_chart import new_fig, finalize, labeled_scatter, TEXT

codes = ['US','CA','FR','UK','DE','AU','SE','FI','NO','PT']
xs    = [2.4, 1.0, 0.66, 0.44, 0.15, 0.44, 0.16, 0.03, 0.05, 0.05]  # Jewish %
ys    = [13.7,23.0,13.1, 14.2, 18.2, 30.1, 20.0,  7.8, 16.1,  8.9]  # Foreign-born %
pop   = [334, 40,  65,   67,   84,   26,   10.5,  5.5, 5.5,  10.3]  # millions

fig, ax = new_fig(figsize=(13, 8.5))
ax.set_xlim(-0.05, 2.6); ax.set_ylim(0, 34)

result = labeled_scatter(
    ax, xs, ys, codes,
    sizes=pop,          # bubble size = population; omit for uniform dots
    ols_line=True,      # dashed regression line in the point color
    stats_box=True,     # r, r², and equation in upper-right box
)

ax.set_xlabel('Jewish % of population', fontsize=16, fontweight='bold', color=TEXT)
ax.set_ylabel('Foreign-born % of population', fontsize=16, fontweight='bold', color=TEXT)
ax.xaxis.set_major_formatter(lambda x, _: f'{x:.1f}%')
ax.yaxis.set_major_formatter(lambda x, _: f'{int(x)}%')
ax.set_title('Jewish population share vs foreign-born share, Western countries',
             fontsize=22, fontweight='bold', pad=32, loc='left')
finalize(fig, "~/charts/<name>.png")
```

Notes:
- **No white rim ever.** `edgecolor='none'` is the default because the rim looked cheap and collided with adjustText labels.
- **Bubble sizes are proportional to `sizes`**, capped at a reasonable range so a huge outlier doesn't dominate.
- **Label collision is auto-handled** by adjustText with thin gray connectors. Don't hand-nudge coordinates.
- **OLS is linear on the natural x-axis**. If you want log-x, set `ax.set_xscale('log')` BEFORE calling `labeled_scatter`, and the OLS line will still be linear-in-x — usually not what you want. For a log-linear fit, drop `ols_line=True` and draw it manually.
