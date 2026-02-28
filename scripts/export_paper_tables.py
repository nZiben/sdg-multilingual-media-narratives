#!/usr/bin/env python3
"""
Export reproducible tables for the EMCSDG 2026 camera-ready paper.

Primary mode (recommended):
  - Uses pandas/pyarrow to read Parquet outputs in data/processed/.

Fallback mode (no scientific deps):
  - Extracts key numbers from the existing Jupyter notebooks/CSVs committed
    to this repo (enough to rebuild the tables used in the paper).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
FULL_WINDOW_START_UTC = "2024-01-01"
FULL_WINDOW_END_UTC = "2025-12-31 23:59:59"

DEFAULTS = {
    "collection_report": REPO_ROOT / "reports" / "01_gdelt_collection_report_2024_2025.json",
    "ipynb_tagging": REPO_ROOT / "02_preprocess_and_sdg_tagging.ipynb",
    "ipynb_analysis": REPO_ROOT / "03_analysis_trends_topics_networks.ipynb",
    "long_parquet": REPO_ROOT / "data" / "processed" / "articles_sdg_long.parquet",
    "tagged_parquet": REPO_ROOT / "data" / "processed" / "articles_tagged.parquet",
    "jsd_csv": REPO_ROOT / "data" / "processed" / "04_language_pairwise_jsd.csv",
    "cluster_terms_csv": REPO_ROOT / "data" / "processed" / "04_cluster_terms.csv",
    "out_dir": REPO_ROOT / "paper" / "tables",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_ipynb(path: Path) -> dict[str, Any]:
    return _read_json(path)


def _iter_output_payloads(ipynb: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for cell in ipynb.get("cells", []):
        for out in cell.get("outputs", []) or []:
            yield out


def _extract_value_counts_from_ipynb(ipynb: dict[str, Any], header: str) -> list[tuple[str, int]]:
    """
    Extract value_counts() outputs rendered as a text/plain block:
      header\n
      KEY  COUNT\n
      ...
    """
    for out in _iter_output_payloads(ipynb):
        data = out.get("data") or {}
        text = data.get("text/plain")
        if not isinstance(text, list):
            continue
        if not text:
            continue
        if str(text[0]).strip() != header:
            continue
        rows: list[tuple[str, int]] = []
        for line in text[1:]:
            line = str(line).strip()
            if not line or line.startswith("Name:"):
                continue
            # e.g. "SDG17_Partnerships          108281"
            m = re.match(r"^(.+?)\s+(\d+)$", line)
            if not m:
                continue
            key = m.group(1).strip()
            val = int(m.group(2))
            rows.append((key, val))
        if rows:
            return rows
    raise RuntimeError(f"Could not find value_counts block for header={header!r} in ipynb.")


def _extract_shape_from_ipynb(ipynb: dict[str, Any], target_shape: str) -> tuple[int, int] | None:
    for out in _iter_output_payloads(ipynb):
        data = out.get("data") or {}
        text = data.get("text/plain")
        if not isinstance(text, list) or not text:
            continue
        if str(text[0]).strip() == target_shape:
            m = re.match(r"^\((\d+),\s*(\d+)\)$", target_shape.strip())
            if m:
                return int(m.group(1)), int(m.group(2))
    return None


def _extract_long_and_tagged_shapes(ipynb_analysis: dict[str, Any]) -> tuple[tuple[int, int], tuple[int, int]]:
    # In Notebook 03 the first code cell output is like: "((182720, 14), (158648, 14))"
    for out in _iter_output_payloads(ipynb_analysis):
        data = out.get("data") or {}
        text = data.get("text/plain")
        if not isinstance(text, list) or not text:
            continue
        s = str(text[0]).strip()
        m = re.match(r"^\(\((\d+),\s*(\d+)\),\s*\((\d+),\s*(\d+)\)\)$", s)
        if not m:
            continue
        long_shape = (int(m.group(1)), int(m.group(2)))
        tagged_shape = (int(m.group(3)), int(m.group(4)))
        return long_shape, tagged_shape
    raise RuntimeError("Could not extract (long.shape, tagged.shape) from analysis notebook outputs.")


def _extract_top_edges_from_ipynb_analysis(ipynb_analysis: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract the displayed HTML table after the 'top edges:' print.
    Returns list of dict rows: source_country, sdg, weight.
    """
    saw_top_edges_marker = False
    for out in _iter_output_payloads(ipynb_analysis):
        if out.get("output_type") == "stream" and out.get("name") == "stdout":
            for t in out.get("text", []) or []:
                if "top edges:" in str(t):
                    saw_top_edges_marker = True
        if not saw_top_edges_marker:
            continue
        data = out.get("data") or {}
        html_lines = data.get("text/html")
        if not isinstance(html_lines, list) or not html_lines:
            continue
        html = "".join(map(str, html_lines))
        if "<table" not in html or "<td>" not in html:
            continue
        cells = re.findall(r"<td>(.*?)</td>", html, flags=re.DOTALL)
        if len(cells) < 3:
            continue
        rows: list[dict[str, Any]] = []
        for i in range(0, len(cells) - 2, 3):
            source_country = re.sub(r"<.*?>", "", cells[i]).strip()
            sdg = re.sub(r"<.*?>", "", cells[i + 1]).strip()
            weight_raw = re.sub(r"<.*?>", "", cells[i + 2]).strip()
            if not source_country or not sdg or not weight_raw:
                continue
            try:
                weight = int(weight_raw)
            except ValueError:
                continue
            rows.append({"source_country": source_country, "sdg": sdg, "weight": weight})
        if rows:
            return rows
    raise RuntimeError("Could not extract top edges table from analysis notebook outputs.")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def _escape_tex(text: str) -> str:
    # Minimal escaping for table cells. Avoid double-escaping already escaped sequences.
    s = str(text)
    s = re.sub(r"(?<!\\)&", r"\\&", s)
    s = re.sub(r"(?<!\\)%", r"\\%", s)
    s = re.sub(r"(?<!\\)\$", r"\\$", s)
    s = re.sub(r"(?<!\\)#", r"\\#", s)
    s = re.sub(r"(?<!\\)_", r"\\_", s)
    s = re.sub(r"(?<!\\)\{", r"\\{", s)
    s = re.sub(r"(?<!\\)\}", r"\\}", s)
    s = s.replace("~", r"\\textasciitilde{}")
    s = s.replace("^", r"\\textasciicircum{}")
    return s


def _write_simple_tex_table(
    path: Path,
    caption: str,
    label: str,
    headers: list[str],
    rows: list[list[str]],
    *,
    colspec: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if colspec is None:
        colspec = "l" * len(headers)
    lines: list[str] = []
    lines.append(r"\begin{table}[H]")
    lines.append(r"\centering")
    lines.append(r"\caption{" + caption + r"}")
    lines.append(r"\label{" + label + r"}")
    lines.append(r"\begin{tabular}{" + colspec + r"}")
    lines.append(r"\toprule")
    lines.append(" & ".join(headers) + r" \\")
    lines.append(r"\midrule")
    for row in rows:
        lines.append(" & ".join(_escape_tex(c) for c in row) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sdg_sort_key(sdg: str) -> tuple[int, str]:
    m = re.match(r"^SDG(\\d+)_", str(sdg))
    if not m:
        return 999, str(sdg)
    return int(m.group(1)), str(sdg)


def _try_primary_mode(args: argparse.Namespace) -> bool:
    try:
        import pandas as pd  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return False

    # Optional: pyarrow is needed to read parquet via pandas.
    try:
        import pyarrow  # noqa: F401  # type: ignore
    except Exception:
        print("pandas found but pyarrow missing; falling back to notebook-extraction mode.", file=sys.stderr)
        return False

    long_path = Path(args.long_parquet)
    tagged_path = Path(args.tagged_parquet)
    if not long_path.exists() or not tagged_path.exists():
        print("Parquet inputs not found; falling back to notebook-extraction mode.", file=sys.stderr)
        return False

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    long = pd.read_parquet(long_path)
    tagged = pd.read_parquet(tagged_path)

    # Enforce full-corpus window (fixes rare out-of-range records like 2026-01).
    start = pd.Timestamp(FULL_WINDOW_START_UTC, tz="UTC")
    end = pd.Timestamp(FULL_WINDOW_END_UTC, tz="UTC")
    for df in (long, tagged):
        if "seendate_utc" not in df.columns:
            continue
        df["seendate_utc"] = pd.to_datetime(df["seendate_utc"], utc=True, errors="coerce")
    if "seendate_utc" in long.columns:
        long = long[(long["seendate_utc"] >= start) & (long["seendate_utc"] <= end)].copy()
    if "seendate_utc" in tagged.columns:
        tagged = tagged[(tagged["seendate_utc"] >= start) & (tagged["seendate_utc"] <= end)].copy()

    # Fill missing source_country from gdelt_raw["sourcecountry"] (common in this repo run).
    if {"source_country", "gdelt_raw"}.issubset(set(long.columns)):
        missing = long["source_country"].isna() | (long["source_country"].astype(str).str.strip() == "")
        if bool(missing.any()):
            import json as _json

            def _extract_sourcecountry(val: Any) -> str | None:
                if val is None or val == "":
                    return None
                if isinstance(val, dict):
                    sc = val.get("sourcecountry")
                else:
                    try:
                        sc = _json.loads(val).get("sourcecountry")
                    except Exception:
                        return None
                if sc is None:
                    return None
                sc = str(sc).strip()
                return sc or None

            long.loc[missing, "source_country"] = long.loc[missing, "gdelt_raw"].map(_extract_sourcecountry)
        long["source_country"] = long["source_country"].astype("string")
        long.loc[long["source_country"].str.strip() == "", "source_country"] = pd.NA

    # Corpus stats
    report = _read_json(Path(args.collection_report))
    total_mentions = int(len(long))
    total_articles = int(len(tagged))
    mean_sdgs = (total_mentions / total_articles) if total_articles else float("nan")
    corpus_rows = [
        {
            "scope": "full_2024_2025",
            "start_utc": report.get("start_utc", ""),
            "end_utc": report.get("end_utc", ""),
            "raw_rows": report.get("raw_rows", ""),
            "dedup_rows": report.get("dedup_rows", ""),
            "sdg_labeled_articles": total_articles,
            "article_sdg_mentions": total_mentions,
            "mean_sdgs_per_article": f"{mean_sdgs:.2f}" if math.isfinite(mean_sdgs) else "",
        }
    ]
    _write_csv(out_dir / "table_corpus_stats.csv", corpus_rows, list(corpus_rows[0].keys()))

    # SDG counts
    sdg_counts = long["sdg"].value_counts().rename_axis("sdg").reset_index(name="mentions")
    sdg_counts["share"] = sdg_counts["mentions"] / total_mentions
    sdg_rows = sdg_counts.to_dict(orient="records")
    _write_csv(out_dir / "table_sdg_counts_full.csv", sdg_rows, ["sdg", "mentions", "share"])

    # Language counts
    lang_counts = long["lang"].value_counts().rename_axis("lang").reset_index(name="mentions")
    lang_counts["share"] = lang_counts["mentions"] / total_mentions
    lang_rows = lang_counts.to_dict(orient="records")
    _write_csv(out_dir / "table_language_counts_full.csv", lang_rows, ["lang", "mentions", "share"])

    # Optional: emit small .tex fragments for \input{}
    try:
        top_n = int(args.top_sdg_rows)
        sdg_top = sdg_counts.head(top_n).copy()
        other_mentions = int(total_mentions - int(sdg_top["mentions"].sum()))
        sdg_tex_rows: list[list[str]] = []
        for _, row in sdg_top.iterrows():
            sdg_tex_rows.append([str(row["sdg"]), f'{int(row["mentions"]):,}', f'{100 * float(row["share"]):.1f}%'])
        if other_mentions > 0:
            sdg_tex_rows.append(["Other SDGs (combined)", f"{other_mentions:,}", f'{100 * (other_mentions / total_mentions):.1f}%'])
        _write_simple_tex_table(
            out_dir / "table_sdg_counts_full.tex",
            caption="Top SDG mention counts and shares in the full 2024--2025 corpus.",
            label="tab:sdg_counts_full",
            headers=["SDG", "Mentions", "Share"],
            rows=sdg_tex_rows,
            colspec="lrr",
        )
    except Exception:
        pass

    # Top country×SDG edges
    if {"source_country", "sdg"}.issubset(set(long.columns)):
        edges = (
            long.dropna(subset=["source_country"])
            .groupby(["source_country", "sdg"])
            .size()
            .rename("weight")
            .reset_index()
            .sort_values("weight", ascending=False)
        )
        top_edges = edges.head(int(args.top_edges)).to_dict(orient="records")
        _write_csv(out_dir / "table_top_country_sdg_edges.csv", top_edges, ["source_country", "sdg", "weight"])

        try:
            edge_rows = [[r["source_country"], r["sdg"], f'{int(r["weight"]):,}'] for r in top_edges]  # type: ignore[index]
            _write_simple_tex_table(
                out_dir / "table_top_country_sdg_edges.tex",
                caption="Top SDG$\\times$country co-occurrence edges (full corpus).",
                label="tab:top_edges",
                headers=["Country", "SDG", "Weight"],
                rows=edge_rows,
                colspec="llr",
            )
        except Exception:
            pass

    # --- New analyses for Paper v2 (A+B+C) ---
    # A) Language agenda divergence (JSD over SDG distributions; top 10 languages)
    if {"lang", "sdg"}.issubset(set(long.columns)):
        all_sdgs = sorted(long["sdg"].dropna().unique().tolist(), key=_sdg_sort_key)
        top_langs = long["lang"].value_counts().head(int(args.top_languages)).index.tolist()

        counts = (
            long[long["lang"].isin(top_langs)]
            .groupby(["lang", "sdg"])
            .size()
            .unstack(fill_value=0)
            .reindex(index=top_langs, columns=all_sdgs, fill_value=0)
        )

        eps = float(args.jsd_epsilon)
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

        jsd_df = pd.DataFrame(jsd_mat, index=top_langs, columns=top_langs)
        jsd_df.to_csv(out_dir / "table_language_sdg_jsd_matrix.csv", index_label="lang")

        pairs: list[dict[str, Any]] = []
        for i in range(len(top_langs)):
            for j in range(i + 1, len(top_langs)):
                pairs.append({"lang_a": top_langs[i], "lang_b": top_langs[j], "jsd": float(jsd_mat[i, j])})
        pairs_sorted = sorted(pairs, key=lambda x: x["jsd"], reverse=True)
        _write_csv(
            out_dir / "table_language_sdg_jsd_pairs_top.csv",
            pairs_sorted[: int(args.top_jsd_pairs)],
            ["lang_a", "lang_b", "jsd"],
        )
        _write_csv(
            out_dir / "table_language_sdg_jsd_pairs_bottom.csv",
            list(reversed(pairs_sorted[-int(args.bottom_jsd_pairs) :])),
            ["lang_a", "lang_b", "jsd"],
        )

        # B) Language SDG portfolio diversity (entropy and effective number)
        entropy = -np.sum(probs * np.log(probs), axis=1)
        eff = np.exp(entropy)
        sdg17 = "SDG17_Partnerships"
        sdg10 = "SDG10_Reduced_Inequalities"
        sdg17_idx = all_sdgs.index(sdg17) if sdg17 in all_sdgs else None
        sdg10_idx = all_sdgs.index(sdg10) if sdg10 in all_sdgs else None

        div_rows: list[dict[str, Any]] = []
        for idx, lang in enumerate(top_langs):
            mentions = int(counts.loc[lang].sum())
            sdg17_share = float(probs[idx, sdg17_idx]) if sdg17_idx is not None else float("nan")
            sdg10_share = float(probs[idx, sdg10_idx]) if sdg10_idx is not None else float("nan")
            div_rows.append(
                {
                    "lang": lang,
                    "mentions": mentions,
                    "sdg17_share": sdg17_share,
                    "sdg10_share": sdg10_share,
                    "entropy": float(entropy[idx]),
                    "effective_sdgs": float(eff[idx]),
                }
            )
        _write_csv(
            out_dir / "table_language_diversity_full.csv",
            div_rows,
            ["lang", "mentions", "sdg17_share", "sdg10_share", "entropy", "effective_sdgs"],
        )
        try:
            div_tex_rows = []
            for r in div_rows:
                div_tex_rows.append(
                    [
                        str(r["lang"]).title(),
                        f'{int(r["mentions"]):,}',
                        f'{100 * float(r["sdg17_share"]):.1f}%',
                        f'{100 * float(r["sdg10_share"]):.1f}%',
                        f'{float(r["entropy"]):.2f}',
                        f'{float(r["effective_sdgs"]):.2f}',
                    ]
                )
            _write_simple_tex_table(
                out_dir / "table_language_diversity_full.tex",
                caption="SDG portfolio diversity by language (top languages; full 2024--2025 corpus).",
                label="tab:lang_diversity",
                headers=["Language", "Mentions", "SDG17 share", "SDG10 share", "Entropy", "Eff. SDGs"],
                rows=div_tex_rows,
                colspec="lrrrrr",
            )
        except Exception:
            pass

    # C) Temporal spike analysis (monthly SDG counts + spike events)
    if {"sdg", "seendate_utc"}.issubset(set(long.columns)):
        long["month"] = long["seendate_utc"].dt.to_period("M").astype(str)
        months = pd.period_range("2024-01", "2025-12", freq="M").astype(str).tolist()
        sdgs = sorted(long["sdg"].dropna().unique().tolist(), key=_sdg_sort_key)

        monthly = (
            long.groupby(["sdg", "month"])
            .size()
            .rename("count")
            .reset_index()
            .pivot_table(index="sdg", columns="month", values="count", fill_value=0)
            .reindex(index=sdgs, columns=months, fill_value=0)
        )

        monthly_long_rows: list[dict[str, Any]] = []
        for sdg in sdgs:
            for month in months:
                monthly_long_rows.append({"sdg": sdg, "month": month, "count": int(monthly.loc[sdg, month])})
        _write_csv(out_dir / "table_sdg_monthly_counts.csv", monthly_long_rows, ["sdg", "month", "count"])

        mu = monthly.mean(axis=1).to_numpy(dtype=float)
        sigma = monthly.std(axis=1, ddof=0).replace(0, np.nan).to_numpy(dtype=float)
        z = (monthly.to_numpy(dtype=float) - mu[:, None]) / sigma[:, None]
        z = np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)
        sdg_total = monthly.sum(axis=1).to_numpy(dtype=float)

        spikes: list[dict[str, Any]] = []
        for i, sdg in enumerate(sdgs):
            if sdg_total[i] < float(args.min_sdg_total_mentions):
                continue
            for j, month in enumerate(months):
                count = float(monthly.iloc[i, j])
                z_ij = float(z[i, j])
                if z_ij < float(args.spike_z_threshold) or count < float(args.min_monthly_mentions):
                    continue

                subset = long[(long["sdg"] == sdg) & (long["month"] == month)]

                top_langs_str = ""
                if "lang" in subset.columns:
                    top_langs = subset["lang"].value_counts().head(3).items()
                    top_langs_str = "; ".join([f"{k} ({int(v)})" for k, v in top_langs])

                top_countries_str = ""
                if "source_country" in subset.columns:
                    top_countries = subset.dropna(subset=["source_country"])["source_country"].value_counts().head(3).items()
                    top_countries_str = "; ".join([f"{k} ({int(v)})" for k, v in top_countries])

                spikes.append(
                    {
                        "month": month,
                        "sdg": sdg,
                        "count": int(count),
                        "z": z_ij,
                        "top_languages": top_langs_str,
                        "top_countries": top_countries_str,
                    }
                )

        spikes_sorted = sorted(spikes, key=lambda x: (x["z"], x["count"]), reverse=True)
        spikes_top = spikes_sorted[: int(args.top_spikes)]
        _write_csv(
            out_dir / "table_sdg_spike_events.csv",
            spikes_top,
            ["month", "sdg", "count", "z", "top_languages", "top_countries"],
        )
        try:
            spike_tex_rows = []
            for r in spikes_top:
                spike_tex_rows.append(
                    [
                        str(r["month"]),
                        str(r["sdg"]),
                        f'{int(r["count"]):,}',
                        f'{float(r["z"]):.2f}',
                        str(r["top_languages"]),
                        str(r["top_countries"]),
                    ]
                )
            _write_simple_tex_table(
                out_dir / "table_sdg_spike_events.tex",
                caption="Detected monthly spike events in SDG attention (full corpus; z-score thresholding).",
                label="tab:spike_events",
                headers=["Month", "SDG", "Mentions", "$z$", "Top languages", "Top countries"],
                rows=spike_tex_rows,
                colspec="llrrp{0.28\\linewidth}p{0.28\\linewidth}",
            )
        except Exception:
            pass

    return True


def _fallback_mode(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = _read_json(Path(args.collection_report))
    ipynb_tagging = _read_ipynb(Path(args.ipynb_tagging))
    ipynb_analysis = _read_ipynb(Path(args.ipynb_analysis))

    (long_n, _), (tagged_n, _) = _extract_long_and_tagged_shapes(ipynb_analysis)
    total_mentions = int(long_n)
    total_articles = int(tagged_n)
    mean_sdgs = (total_mentions / total_articles) if total_articles else float("nan")

    corpus_rows = [
        {
            "scope": "full_2024_2025",
            "start_utc": report.get("start_utc", ""),
            "end_utc": report.get("end_utc", ""),
            "raw_rows": report.get("raw_rows", ""),
            "dedup_rows": report.get("dedup_rows", ""),
            "sdg_labeled_articles": total_articles,
            "article_sdg_mentions": total_mentions,
            "mean_sdgs_per_article": f"{mean_sdgs:.2f}" if math.isfinite(mean_sdgs) else "",
        }
    ]
    _write_csv(out_dir / "table_corpus_stats.csv", corpus_rows, list(corpus_rows[0].keys()))

    # SDG counts (top 10 from notebook + "Other")
    sdg_top = _extract_value_counts_from_ipynb(ipynb_tagging, header="sdg")
    sdg_rows: list[dict[str, Any]] = []
    top_sum = 0
    for sdg, mentions in sdg_top:
        top_sum += mentions
        sdg_rows.append({"sdg": sdg, "mentions": mentions, "share": mentions / total_mentions})
    other = total_mentions - top_sum
    if other > 0:
        sdg_rows.append({"sdg": "Other_SDGs_combined", "mentions": other, "share": other / total_mentions})
    _write_csv(out_dir / "table_sdg_counts_full.csv", sdg_rows, ["sdg", "mentions", "share"])

    # Language counts (top 10 from notebook + "Other")
    lang_top = _extract_value_counts_from_ipynb(ipynb_tagging, header="lang")
    lang_rows: list[dict[str, Any]] = []
    top_sum = 0
    for lang, mentions in lang_top:
        top_sum += mentions
        lang_rows.append({"lang": lang, "mentions": mentions, "share": mentions / total_mentions})
    other = total_mentions - top_sum
    if other > 0:
        lang_rows.append({"lang": "other", "mentions": other, "share": other / total_mentions})
    _write_csv(out_dir / "table_language_counts_full.csv", lang_rows, ["lang", "mentions", "share"])

    # Top edges (from notebook HTML table)
    top_edges = _extract_top_edges_from_ipynb_analysis(ipynb_analysis)
    _write_csv(out_dir / "table_top_country_sdg_edges.csv", top_edges[: int(args.top_edges)], ["source_country", "sdg", "weight"])

    # Pilot JSD (top/bottom pairs)
    jsd_path = Path(args.jsd_csv)
    if jsd_path.exists():
        with jsd_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            jsd_rows = [
                {"lang_a": row["lang_a"], "lang_b": row["lang_b"], "jsd": float(row["jsd"])}
                for row in r
                if row.get("lang_a") and row.get("lang_b") and row.get("jsd")
            ]
        jsd_rows_sorted = sorted(jsd_rows, key=lambda x: x["jsd"], reverse=True)
        top = jsd_rows_sorted[: int(args.top_jsd)]
        bottom = list(reversed(jsd_rows_sorted[-int(args.bottom_jsd) :]))
        _write_csv(out_dir / "table_jsd_top_pairs.csv", top, ["lang_a", "lang_b", "jsd"])
        _write_csv(out_dir / "table_jsd_bottom_pairs.csv", bottom, ["lang_a", "lang_b", "jsd"])

    # Cluster frame families (top clusters by n)
    cluster_path = Path(args.cluster_terms_csv)
    if cluster_path.exists():
        with cluster_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            clusters = []
            for row in r:
                try:
                    clusters.append(
                        {
                            "cluster": int(row["cluster"]),
                            "n": int(row["n"]),
                            "top_terms": row["top_terms"],
                        }
                    )
                except Exception:
                    continue
        clusters_sorted = sorted(clusters, key=lambda x: x["n"], reverse=True)
        top_clusters = clusters_sorted[: int(args.top_clusters)]
        _write_csv(out_dir / "table_cluster_frame_families.csv", top_clusters, ["cluster", "n", "top_terms"])

    # Optional: emit small .tex fragments for \input{}
    try:
        sdg_tex_rows = [[r["sdg"], str(r["mentions"]), f'{float(r["share"]):.3f}'] for r in sdg_rows]
        _write_simple_tex_table(
            out_dir / "table_sdg_counts_full.tex",
            caption="Top SDG mention counts and shares (full 2024--2025 corpus).",
            label="tab:sdg_counts_full",
            headers=["SDG", "Mentions", "Share"],
            rows=sdg_tex_rows,
        )
        lang_tex_rows = [[r["lang"], str(r["mentions"]), f'{float(r["share"]):.3f}'] for r in lang_rows]
        _write_simple_tex_table(
            out_dir / "table_language_counts_full.tex",
            caption="Top language mention counts and shares (full 2024--2025 corpus).",
            label="tab:lang_counts_full",
            headers=["Language", "Mentions", "Share"],
            rows=lang_tex_rows,
        )
    except Exception:
        # Non-fatal; paper can still be written using the CSVs.
        pass


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--collection-report", default=str(DEFAULTS["collection_report"]))
    p.add_argument("--ipynb-tagging", default=str(DEFAULTS["ipynb_tagging"]))
    p.add_argument("--ipynb-analysis", default=str(DEFAULTS["ipynb_analysis"]))
    p.add_argument("--long-parquet", default=str(DEFAULTS["long_parquet"]))
    p.add_argument("--tagged-parquet", default=str(DEFAULTS["tagged_parquet"]))
    p.add_argument("--jsd-csv", default=str(DEFAULTS["jsd_csv"]))
    p.add_argument("--cluster-terms-csv", default=str(DEFAULTS["cluster_terms_csv"]))
    p.add_argument("--out-dir", default=str(DEFAULTS["out_dir"]))
    p.add_argument("--top-edges", type=int, default=15)
    p.add_argument("--top-sdg-rows", type=int, default=10)
    p.add_argument("--top-languages", type=int, default=10)
    p.add_argument("--jsd-epsilon", type=float, default=1e-12)
    p.add_argument("--top-jsd-pairs", type=int, default=10)
    p.add_argument("--bottom-jsd-pairs", type=int, default=10)
    p.add_argument("--spike-z-threshold", type=float, default=2.5)
    p.add_argument("--min-monthly-mentions", type=int, default=50)
    p.add_argument("--min-sdg-total-mentions", type=int, default=1000)
    p.add_argument("--top-spikes", type=int, default=15)
    p.add_argument("--top-jsd", type=int, default=10)
    p.add_argument("--bottom-jsd", type=int, default=10)
    p.add_argument("--top-clusters", type=int, default=15)
    args = p.parse_args()

    if _try_primary_mode(args):
        return 0

    _fallback_mode(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
