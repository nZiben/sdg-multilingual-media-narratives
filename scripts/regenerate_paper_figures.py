#!/usr/bin/env python3
"""
Prepare camera-ready paper figures under paper/figures/.

Paper v2 figures (main paper):
  - Fig 2: Total SDG mentions per month (2024–2025)
  - Fig 3: Language agenda divergence (JSD heatmap over SDG distributions)
  - Fig 4: Temporal spike heatmap (monthly z-scores for selected SDGs)

This script requires scientific Python deps (pandas, pyarrow, matplotlib, seaborn).
Run with the system Python on macOS: /usr/bin/python3.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LONG_PARQUET = REPO_ROOT / "data" / "processed" / "articles_sdg_long.parquet"
FULL_WINDOW_START_UTC = "2024-01-01"
FULL_WINDOW_END_UTC = "2025-12-31 23:59:59"

def _save_png_pdf(fig, png_path: Path, pdf_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")


def _sdg_sort_key(sdg: str) -> tuple[int, str]:
    import re

    m = re.match(r"^SDG(\\d+)_", str(sdg))
    if not m:
        return 999, str(sdg)
    return int(m.group(1)), str(sdg)


def _pretty_sdg_label(sdg: str) -> str:
    import re

    m = re.match(r"^SDG(\\d+)_(.+)$", str(sdg))
    if not m:
        return str(sdg)
    num = m.group(1)
    name = m.group(2).replace("_", " ")
    return f"SDG {num} {name}"


def _try_regenerate_from_parquet(out_dir: Path) -> bool:
    """
    Best-effort regeneration when scientific deps exist.
    Returns True if at least the core paper figures were regenerated.
    """
    try:
        import pandas as pd  # type: ignore
        import numpy as np  # type: ignore
        import matplotlib  # type: ignore

        matplotlib.use("Agg")  # headless-safe
        import matplotlib.pyplot as plt  # type: ignore
        import seaborn as sns  # type: ignore
        import pyarrow  # noqa: F401  # type: ignore
    except Exception:
        return False

    if not LONG_PARQUET.exists():
        return False

    long = pd.read_parquet(LONG_PARQUET)
    if "seendate_utc" not in long.columns:
        return False

    # Enforce window to avoid out-of-range month artifacts (e.g., 2026-01).
    start = pd.Timestamp(FULL_WINDOW_START_UTC, tz="UTC")
    end = pd.Timestamp(FULL_WINDOW_END_UTC, tz="UTC")
    long["seendate_utc"] = pd.to_datetime(long["seendate_utc"], utc=True, errors="coerce")
    long = long[(long["seendate_utc"] >= start) & (long["seendate_utc"] <= end)].copy()
    if len(long) == 0:
        return False

    long["month"] = long["seendate_utc"].dt.to_period("M").astype(str)
    months = pd.period_range("2024-01", "2025-12", freq="M").astype(str).tolist()
    out_dir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", context="paper")

    # Fig 2: total mentions per month
    month_counts = long.groupby("month").size().reindex(months, fill_value=0)
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.plot(month_counts.index, month_counts.values, linewidth=2, marker="o", markersize=3)
    ax.set_title("Total SDG mentions per month (2024–2025)")
    ax.set_ylabel("Article–SDG mentions")
    ax.set_xlabel("Month (UTC)")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    _save_png_pdf(fig, out_dir / "fig02_total_mentions_per_month.png", out_dir / "fig02_total_mentions_per_month.pdf")
    plt.close(fig)

    if not {"lang", "sdg"}.issubset(set(long.columns)):
        return False

    # Fig 3: Language agenda divergence (JSD over SDG distributions; top 10 languages)
    all_sdgs = sorted(long["sdg"].dropna().unique().tolist(), key=_sdg_sort_key)
    top_langs = long["lang"].value_counts().head(10).index.tolist()
    counts = (
        long[long["lang"].isin(top_langs)]
        .groupby(["lang", "sdg"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=top_langs, columns=all_sdgs, fill_value=0)
    )
    eps = 1e-12
    counts_np = counts.to_numpy(dtype=float)
    probs = (counts_np + eps) / (counts_np.sum(axis=1, keepdims=True) + eps * len(all_sdgs))

    def _jsd(p: np.ndarray, q: np.ndarray) -> float:
        m = 0.5 * (p + q)
        kl_pm = float(np.sum(p * np.log(p / m)))
        kl_qm = float(np.sum(q * np.log(q / m)))
        return 0.5 * (kl_pm + kl_qm)

    jsd_mat = np.zeros((len(top_langs), len(top_langs)), dtype=float)
    for i in range(len(top_langs)):
        for j in range(i + 1, len(top_langs)):
            v = _jsd(probs[i], probs[j])
            jsd_mat[i, j] = v
            jsd_mat[j, i] = v

    jsd_df = pd.DataFrame(jsd_mat, index=[l.title() for l in top_langs], columns=[l.title() for l in top_langs])
    fig, ax = plt.subplots(figsize=(7.2, 6.3))
    sns.heatmap(
        jsd_df,
        ax=ax,
        cmap="cividis",
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        linecolor="white",
        square=True,
        cbar_kws={"label": "Jensen–Shannon divergence"},
    )
    ax.set_title("Language agenda divergence (JSD over SDG distributions, 2024–2025)")
    ax.set_xlabel("")
    ax.set_ylabel("")
    _save_png_pdf(fig, out_dir / "fig03_language_sdg_jsd_heatmap.png", out_dir / "fig03_language_sdg_jsd_heatmap.pdf")
    plt.close(fig)

    # Fig 4: Temporal spike heatmap (z-scores over monthly SDG counts; selected SDGs)
    monthly = (
        long.groupby(["sdg", "month"])
        .size()
        .rename("count")
        .reset_index()
        .pivot_table(index="sdg", columns="month", values="count", fill_value=0)
        .reindex(index=all_sdgs, columns=months, fill_value=0)
    )
    mu = monthly.mean(axis=1)
    sigma = monthly.std(axis=1, ddof=0).replace(0, np.nan)
    z = (monthly.sub(mu, axis=0)).div(sigma, axis=0).fillna(0.0)

    selected_sdgs = [
        "SDG17_Partnerships",
        "SDG3_Good_Health",
        "SDG13_Climate_Action",
        "SDG7_Clean_Energy",
        "SDG5_Gender_Equality",
        "SDG1_No_Poverty",
        "SDG4_Quality_Education",
        "SDG8_Decent_Work",
        "SDG9_Industry_Innovation",
        "SDG10_Reduced_Inequalities",
    ]
    present_sdgs = [s for s in selected_sdgs if s in z.index]
    z_sel = z.loc[present_sdgs, months].copy()
    z_pos = z_sel.clip(lower=0.0)

    fig, ax = plt.subplots(figsize=(11, 3.9))
    sns.heatmap(
        z_pos,
        ax=ax,
        cmap="Greys",
        vmin=0.0,
        vmax=max(3.5, float(z_pos.to_numpy().max()) if z_pos.size else 3.5),
        cbar_kws={"label": "Monthly z-score (clipped at 0)"},
        linewidths=0.35,
        linecolor="white",
    )
    ax.set_title("Punctuated SDG attention: monthly spikes (2024–2025)")
    ax.set_xlabel("Month (UTC)")
    ax.set_ylabel("")
    ax.set_yticklabels([_pretty_sdg_label(s) for s in present_sdgs], rotation=0)
    ax.tick_params(axis="x", rotation=45, labelsize=8)

    # Outline detected spikes for readability in grayscale.
    from matplotlib.patches import Rectangle  # type: ignore

    sdg_total = monthly.sum(axis=1)
    for i, sdg in enumerate(present_sdgs):
        if float(sdg_total.get(sdg, 0)) < 1000:
            continue
        for j, month in enumerate(months):
            count = float(monthly.loc[sdg, month])
            z_ij = float(z.loc[sdg, month])
            if z_ij >= 2.5 and count >= 50:
                ax.add_patch(Rectangle((j, i), 1, 1, fill=False, edgecolor="black", linewidth=1.0))

    _save_png_pdf(fig, out_dir / "fig04_sdg_spike_heatmap.png", out_dir / "fig04_sdg_spike_heatmap.pdf")
    plt.close(fig)

    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=str(REPO_ROOT / "paper" / "figures"))
    args = p.parse_args()

    out_dir = Path(args.out_dir)

    if _try_regenerate_from_parquet(out_dir):
        return 0

    print("ERROR: Cannot regenerate figures without scientific Python deps.", file=sys.stderr)
    print("Hint: run with /usr/bin/python3 scripts/regenerate_paper_figures.py", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
