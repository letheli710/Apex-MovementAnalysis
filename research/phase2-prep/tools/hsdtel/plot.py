"""Dependency-free SVG line plots (matplotlib PNG output when it is installed)."""
import html
import math

PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#4b5563", "#ca8a04"]


def _nice_ticks(lo, hi, n=6):
    if not (math.isfinite(lo) and math.isfinite(hi)) or hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=mag * 10)
    start = math.floor(lo / step) * step
    ticks, v = [], start
    while v <= hi + step * 0.5:
        ticks.append(round(v, 10))
        v += step
    return ticks


def svg_plot(series, title="", xlabel="", ylabel="", markers=None, width=960, height=420):
    """series: [(label, [(x, y), ...])]; markers: [(x, label)] vertical lines."""
    pts = [(x, y) for _, s in series for x, y in s if math.isfinite(x) and math.isfinite(y)]
    if not pts:
        pts = [(0.0, 0.0), (1.0, 1.0)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    xt, yt = _nice_ticks(min(xs), max(xs)), _nice_ticks(min(min(ys), 0.0), max(ys))
    x0, x1, y0, y1 = xt[0], xt[-1], yt[0], yt[-1]
    ml, mr, mt, mb = 70, 170, 40, 50
    pw, ph = width - ml - mr, height - mt - mb

    def X(x):
        return ml + (x - x0) / (x1 - x0 or 1) * pw

    def Y(y):
        return mt + ph - (y - y0) / (y1 - y0 or 1) * ph

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'font-family="sans-serif" font-size="12">',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<text x="{ml}" y="22" font-size="15" font-weight="bold">{html.escape(title)}</text>']
    for t in xt:
        out.append(f'<line x1="{X(t):.1f}" y1="{mt}" x2="{X(t):.1f}" y2="{mt + ph}" stroke="#e5e7eb"/>')
        out.append(f'<text x="{X(t):.1f}" y="{mt + ph + 16}" text-anchor="middle" fill="#374151">{t:g}</text>')
    for t in yt:
        out.append(f'<line x1="{ml}" y1="{Y(t):.1f}" x2="{ml + pw}" y2="{Y(t):.1f}" stroke="#e5e7eb"/>')
        out.append(f'<text x="{ml - 6}" y="{Y(t) + 4:.1f}" text-anchor="end" fill="#374151">{t:g}</text>')
    out.append(f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="none" stroke="#9ca3af"/>')
    out.append(f'<text x="{ml + pw / 2}" y="{height - 10}" text-anchor="middle">{html.escape(xlabel)}</text>')
    out.append(f'<text x="16" y="{mt + ph / 2}" text-anchor="middle" transform="rotate(-90 16 {mt + ph / 2})">'
               f'{html.escape(ylabel)}</text>')
    for x, label in markers or []:
        if x0 <= x <= x1:
            out.append(f'<line x1="{X(x):.1f}" y1="{mt}" x2="{X(x):.1f}" y2="{mt + ph}" stroke="#9ca3af" '
                       f'stroke-dasharray="3,3"><title>{html.escape(str(label))}</title></line>')
    for i, (label, s) in enumerate(series):
        color = PALETTE[i % len(PALETTE)]
        good = [(x, y) for x, y in s if math.isfinite(x) and math.isfinite(y)]
        if good:
            d = " ".join(f"{'M' if j == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for j, (x, y) in enumerate(good))
            out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.5"/>')
        ly = mt + 14 + i * 18
        out.append(f'<rect x="{ml + pw + 12}" y="{ly - 9}" width="12" height="3" fill="{color}"/>')
        out.append(f'<text x="{ml + pw + 30}" y="{ly}">{html.escape(str(label))}</text>')
    out.append("</svg>")
    return "\n".join(out)


def save_png(series, path, title="", xlabel="", ylabel=""):
    """Optional: returns False when matplotlib is not installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for label, s in series:
        ax.plot([p[0] for p in s], [p[1] for p in s], label=str(label), linewidth=1.2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True
