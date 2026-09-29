"""
sm_chart — {{YOUR_NAME}}'s dark-theme chart toolkit.

Purpose: make charts that are READABLE. The #1 rule here is that text never
overlaps, and that rule is ENFORCED, not eyeballed: `finalize()` measures the
pixel bounding box of every text element and raises if any two collide.

Usage:
    from sm_chart import BG, PANEL, COLORS, new_fig, smart_xticks, label_points, finalize
    fig, ax = new_fig()
    ax.bar(...)
    smart_xticks(ax, labels)
    finalize(fig, "~/charts/my_chart.png", source="Census ACS")
"""
import os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# ---- palette ---------------------------------------------------------------
BG    = "#000000"   # figure background — pure black
PANEL = "#000000"   # axes background — pure black
GRID  = "#2a2a2a"   # gridlines
TEXT  = "#ffffff"   # titles, value labels, tick labels, pure white for readability
MUTED = "#e3e3e3"   # secondary text (axis labels, source line, n labels) — near-white
ATTR  = "#ffffff"   # attribution line — pure white
# categorical accents — Claude orange first (default), colorblind-safe on dark
COLORS = ["#D97757", "#69a7df", "#7dbf52", "#ffc933", "#c678dd", "#a9d18e", "#e06c75"]

_FONT = next((f for f in ["Helvetica Neue", "Helvetica", "Avenir Next", "Arial"]
              if f in {x.name for x in fm.fontManager.ttflist}), "DejaVu Sans")


def apply_theme():
    """Global rcParams. constrained_layout is ON so matplotlib auto-spaces elements."""
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": PANEL,
        "font.family": _FONT, "font.size": 13,
        "text.color": TEXT, "axes.labelcolor": MUTED,
        "xtick.color": TEXT, "ytick.color": TEXT,
        "axes.edgecolor": GRID, "axes.titlecolor": TEXT,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 0.08,
        "figure.constrained_layout.w_pad": 0.08,
        "savefig.facecolor": BG, "figure.dpi": 110,
    })


def new_fig(figsize=(12, 7), footer=0.07):
    """Create a themed fig/ax. Reserves a bottom strip so the footer/attribution
    never overlaps the plot (constrained_layout is told to avoid that band)."""
    apply_theme()
    fig, ax = plt.subplots(figsize=figsize, layout="constrained")
    fig.set_facecolor(BG); ax.set_facecolor(PANEL)
    # rect = (left, bottom, width, height) in figure fraction — keeps axes above footer
    fig.get_layout_engine().set(rect=(0.012, footer, 0.976, 0.985 - footer))
    style_axes(ax)
    return fig, ax


def style_axes(ax, grid_axis="y"):
    # Hide top/right; keep left/bottom as visible frame lines with tick marks.
    ax.spines[["top", "right"]].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color("#5a5a5a")
        ax.spines[side].set_linewidth(1.2)
    ax.tick_params(axis="both", length=4, width=1, color="#5a5a5a", labelsize=12)
    if grid_axis in ("y", "both"):
        ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    if grid_axis in ("x", "both"):
        ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    return ax


def smart_xticks(ax, labels, max_horizontal_chars=11, wrap=14):
    """Pick x-tick orientation so labels don't collide.
    - short + few  -> horizontal
    - long         -> rotate 30deg, right-anchored
    - very long    -> wrap onto two lines AND rotate
    For >7 long categories, prefer a horizontal bar chart instead (see hbar())."""
    labels = [str(l) for l in labels]
    longest = max((len(l) for l in labels), default=0)
    ax.set_xticks(range(len(labels)))
    if longest <= max_horizontal_chars:
        ax.set_xticklabels(labels, rotation=0, ha="center")
    else:
        wrapped = ["\n".join(textwrap.wrap(l, wrap)) if len(l) > wrap else l for l in labels]
        ax.set_xticklabels(wrapped, rotation=30, ha="right", rotation_mode="anchor")
    return ax


def hbar(ax, labels, values, color=COLORS[0], sort=True, fmt="{:.0f}", pad_frac=0.02):
    """Horizontal bars — the safest layout for many/long category labels.
    Value labels sit just past each bar end and never overlap."""
    pairs = list(zip(labels, values))
    if sort:
        pairs.sort(key=lambda p: p[1])
    labs, vals = zip(*pairs)
    y = range(len(labs))
    ax.barh(list(y), list(vals), color=color, zorder=3)
    ax.set_yticks(list(y)); ax.set_yticklabels([str(l) for l in labs], fontsize=12)
    style_axes(ax, grid_axis="x")
    span = max(vals) - min(0, min(vals)) or 1
    for yi, v in zip(y, vals):
        ax.text(v + span * pad_frac, yi, fmt.format(v), va="center", ha="left",
                color=TEXT, fontsize=11, fontweight="bold")
    ax.margins(x=0.12)
    return ax


# ---- high-leverage helpers ------------------------------------------------
YELLOW = "#ecbb3a"  # for annotation arrows / callouts


def paired_value_bars(ax, x_positions, values, big_labels=None, small_labels=None,
                      colors=None, width=0.40, big_fs=26, small_fs=13,
                      big_gap=0.35, small_gap=1.55):
    """Bar chart with two label tiers stacked above each bar at uniform offsets.

    big_labels (e.g. percentages) sit `big_gap` above the bar top.
    small_labels (e.g. "n of total") sit `small_gap` above the bar top.
    Uses uniform y-offsets so paired bars look symmetric regardless of value.
    Returns the bar container."""
    n = len(values)
    if colors is None:
        colors = [COLORS[0]] * n
    bars = ax.bar(x_positions, values, width=width, color=colors, alpha=0.97, zorder=3)
    if big_labels is not None:
        for x, v, lab in zip(x_positions, values, big_labels):
            ax.text(x, v + big_gap, lab, ha='center', va='bottom',
                    color=TEXT, fontsize=big_fs, fontweight='bold', zorder=4)
    if small_labels is not None:
        for x, v, lab in zip(x_positions, values, small_labels):
            ax.text(x, v + small_gap, lab, ha='center', va='bottom',
                    color=TEXT, fontsize=small_fs, zorder=4)
    return bars


def callout_arrow(ax, start_xy, end_xy, label=None, color=YELLOW, rad=0.42,
                  lw=2.4, mutation_scale=26, label_xy=None, label_fs=17):
    """Curved arrow from start_xy to end_xy with optional label near the arc.

    label_xy: explicit (x, y) for the label. If None, places label at the midpoint
    of the bounding box biased toward the upper side of the arc."""
    from matplotlib.patches import FancyArrowPatch
    arrow = FancyArrowPatch(start_xy, end_xy,
                            connectionstyle=f'arc3,rad={rad}', arrowstyle='->',
                            mutation_scale=mutation_scale, color=color, lw=lw, zorder=4)
    ax.add_patch(arrow)
    if label:
        if label_xy is None:
            mx = (start_xy[0] + end_xy[0]) / 2
            my = max(start_xy[1], end_xy[1]) * 0.6 + min(start_xy[1], end_xy[1]) * 0.4
            label_xy = (mx + 0.05, my)
        ax.text(label_xy[0], label_xy[1], label, ha='center',
                color=color, fontsize=label_fs, fontweight='bold', zorder=5)
    return arrow


def stacked_bar_with_totals(ax, x_positions, segments, colors, labels=None,
                            width=0.62, min_seg_label=2, total_gap=0.6, total_fs=13,
                            seg_fs=12):
    """Stacked bars with per-segment value labels and a total label on top.

    segments: list of arrays, one per stack layer (bottom to top).
    colors: list of colors, one per layer.
    labels: list of layer names for legend (optional).
    min_seg_label: segments with value < this don't get an inline label (avoids clutter
    for tiny slivers; segments == 1 still get a small label).
    Returns the totals array so caller can set ylim."""
    n_layers = len(segments)
    n_bars = len(x_positions)
    import numpy as _np
    segs = [_np.asarray(s) for s in segments]
    bottoms = _np.zeros(n_bars)
    for i, (s, c) in enumerate(zip(segs, colors)):
        lbl = labels[i] if labels else None
        ax.bar(x_positions, s, width, color=c, bottom=bottoms, label=lbl, zorder=3)
        for x, v, b in zip(x_positions, s, bottoms):
            if v >= min_seg_label:
                ax.text(x, b + v/2, f'{int(v)}', ha='center', va='center',
                        color='#ffffff', fontsize=seg_fs, zorder=4)
            elif v == 1:
                ax.text(x, b + v/2, '1', ha='center', va='center',
                        color='#ffffff', fontsize=seg_fs - 1, zorder=4)
        bottoms = bottoms + s
    for x, t in zip(x_positions, bottoms):
        ax.text(x, t + total_gap, f'{int(t)}', ha='center', va='bottom',
                color=TEXT, fontsize=total_fs, zorder=4)
    return bottoms


def grouped_bars_with_ci(ax, x_positions, group_values, group_los, group_his,
                        colors, group_labels=None, width=0.38,
                        label_fs=14, label_gap_frac=0.05):
    """Grouped bars (typically 2 groups side-by-side) with Wilson/CI whiskers.

    group_values: list of value arrays (one per group).
    group_los, group_his: list of low/high CI arrays.
    Returns list of bar containers."""
    import numpy as _np
    n_groups = len(group_values)
    n_cats = len(x_positions)
    bars_out = []
    offsets = (_np.arange(n_groups) - (n_groups - 1) / 2) * width
    y_max_so_far = 0
    for i in range(n_groups):
        vals = _np.asarray(group_values[i])
        los  = _np.asarray(group_los[i])
        his  = _np.asarray(group_his[i])
        err = [vals - los, his - vals]
        lbl = group_labels[i] if group_labels else None
        b = ax.bar(_np.asarray(x_positions) + offsets[i], vals, width,
                   color=colors[i], alpha=0.92, zorder=3, label=lbl,
                   yerr=err, capsize=4, ecolor='#ffffff',
                   error_kw={'elinewidth': 1.4})
        bars_out.append(b)
        for x, v, hi in zip(_np.asarray(x_positions) + offsets[i], vals, his):
            ax.text(x, hi + 1.0, f'{v:.1f}%', ha='center', va='bottom',
                    color='#ffffff', fontsize=label_fs, fontweight='bold', zorder=4)
        y_max_so_far = max(y_max_so_far, max(his))
    return bars_out


def label_points(ax, xs, ys, texts, fontsize=11, color=TEXT):
    """Scatter/line point labels with automatic collision avoidance (adjustText)."""
    from adjustText import adjust_text
    objs = [ax.text(x, y, str(t), fontsize=fontsize, color=color)
            for x, y, t in zip(xs, ys, texts)]
    adjust_text(objs, ax=ax,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7),
                expand=(1.15, 1.4))
    return objs


def labeled_scatter(ax, xs, ys, labels, sizes=None, color=None, alpha=0.95,
                    label_fs=12, label_bold=True, connector_color="#888888",
                    connector_alpha=0.7, ols_line=False, stats_box=False,
                    expand=(1.35, 1.5)):
    """One-call scatter with auto-placed labels, no white rim, optional OLS fit + stats box.

    Handles all the friction from making a country/state scatter chart:
    - No edgecolor by default (matches house preference: no white rim on points)
    - Labels auto-placed via adjustText with thin gray connectors
    - Optional bubble sizing via `sizes` (numpy array or list; scaled to reasonable range)
    - Optional OLS regression line drawn in same color as points
    - Optional stats box in upper-right with r, r², and OLS equation

    sizes: raw magnitudes (e.g. population). Function scales to 30–880 px^2 range.
           If None, uniform 90 px^2.
    color: point color. Defaults to COLORS[0] (Claude orange). Also used for OLS line.
    ols_line, stats_box: pair these together for the country-scatter pattern.

    Returns: dict with 'scatter', 'texts', and (if ols_line) 'r', 'r2', 'slope', 'intercept'.
    """
    import numpy as np
    from adjustText import adjust_text

    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if color is None:
        color = COLORS[0]
    if sizes is None:
        s = 90
    else:
        s_arr = np.asarray(sizes, dtype=float)
        s = 30 + (s_arr / s_arr.max()) * 850

    sc = ax.scatter(xs, ys, s=s, color=color, alpha=alpha, edgecolor="none", zorder=4)

    texts = [ax.text(x, y, str(l), fontsize=label_fs, color=TEXT,
                     fontweight=("bold" if label_bold else "normal"),
                     ha="center", va="center", zorder=5)
             for x, y, l in zip(xs, ys, labels)]
    adjust_text(
        texts, ax=ax, x=list(xs), y=list(ys), expand=expand,
        arrowprops=dict(arrowstyle="-", color=connector_color, lw=0.7, alpha=connector_alpha),
        force_text=(0.6, 0.9), force_points=(0.35, 0.55),
        only_move={"points": "y", "text": "xy"},
    )

    out = {"scatter": sc, "texts": texts}

    if ols_line or stats_box:
        slope, intercept = np.polyfit(xs, ys, 1)
        r = float(np.corrcoef(xs, ys)[0, 1])
        r2 = r * r
        out.update({"r": r, "r2": r2, "slope": slope, "intercept": intercept})
        if ols_line:
            xlo, xhi = ax.get_xlim()
            x_fit = np.linspace(xlo, xhi, 60)
            ax.plot(x_fit, slope * x_fit + intercept, color=color, linestyle="--",
                    linewidth=1.6, alpha=0.6, zorder=2)
        if stats_box:
            box = f"r = {r:+.3f}   r² = {r2:.3f}\ny = {slope:+.2f}x + {intercept:.2f}"
            ax.text(0.98, 0.96, box, transform=ax.transAxes, ha="right", va="top",
                    color=TEXT, fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1a1a",
                              edgecolor="#5a5a5a", linewidth=1))
    return out


# ---- the enforcement: text must not overlap --------------------------------
def find_overlaps(fig, min_area_px=6.0):
    """Return list of (textA, textB) whose rendered bounding boxes overlap by
    more than min_area_px square pixels. Empty list == clean chart."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = []
    artists = list(fig.texts)
    for ax in fig.axes:
        artists += list(ax.texts)
        artists += ax.get_xticklabels() + ax.get_yticklabels()
        artists += [ax.title, ax.xaxis.label, ax.yaxis.label]
        leg = ax.get_legend()
        if leg:
            artists += leg.get_texts()
    for t in artists:
        if t is None or not t.get_visible():
            continue
        s = (t.get_text() or "").strip()
        if not s:
            continue
        try:
            bb = t.get_window_extent(renderer=r)
        except Exception:
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        items.append((t, bb, s))
    out = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][1], items[j][1]
            ix = max(0, min(a.x1, b.x1) - max(a.x0, b.x0))
            iy = max(0, min(a.y1, b.y1) - max(a.y0, b.y0))
            if ix * iy > min_area_px:
                out.append((items[i][2], items[j][2]))
    return out


def finalize(fig, path, source=None, attribution="{{YOUR_NAME}}",
             dpi=200, strict=True):
    """Add source + attribution, ENFORCE no-overlap, save, and open.
    Raises AssertionError listing the colliding text if anything overlaps
    (set strict=False to warn instead of raise)."""
    path = os.path.expanduser(path)
    if source:
        fig.text(0.012, 0.015, f"Source: {source}", ha="left", va="bottom",
                 color=MUTED, fontsize=10, style="italic")
    if attribution:
        fig.text(0.988, 0.015, attribution, ha="right", va="bottom",
                 color=ATTR, fontsize=11, style="italic")
    overlaps = find_overlaps(fig)
    if overlaps:
        msg = "TEXT OVERLAP DETECTED — fix before shipping:\n" + "\n".join(
            f"  • {a!r}  ⟷  {b!r}" for a, b in overlaps)
        if strict:
            raise AssertionError(msg)
        print(msg)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=BG)
    print(f"saved {path}  ({'CLEAN' if not overlaps else str(len(overlaps))+' overlaps'})")
    os.system(f'open "{path}"')
    return path
