"""Session 1: ingest and light cleaning for NSMES1988 dataset.

Uses pandas and standard library only. Provides small, testable functions
for loading, inspecting schema, recommending dtypes, applying dtype
changes, and exporting results and a markdown report.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import DataFrame
from pandas.api import types as ptypes

LOG = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler()],
    )


def load_csv(path: Path) -> DataFrame:
    """Load CSV located at `path`.

    Exits gracefully with a clear message if file is missing.
    """
    LOG.info("Loading CSV from %s", path)
    if not path.exists():
        LOG.error("Input CSV not found: %s", path)
        print(f"Input CSV not found: {path}")
        print(f"Aborting. Please ensure the file exists at the specified path.")
        sys.exit(1)
    df = pd.read_csv(path)
    LOG.info("Loaded %d rows, %d columns", df.shape[0], df.shape[1])
    return df


def inspect_schema(df: DataFrame) -> Dict[str, Any]:
    """Return basic schema info: rows, columns, dtypes, missing counts."""
    rows, cols = df.shape
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    missing = df.isna().sum().to_dict()
    info = {
        "rows": int(rows),
        "columns": int(cols),
        "dtypes": dtypes,
        "missing": {k: int(v) for k, v in missing.items()},
    }
    return info


def recommend_dtypes(df: DataFrame) -> Dict[str, Dict[str, str]]:
    """Recommend dtype changes.

    Returns a mapping column -> {"recommended": dtype, "reason": str}.
    """
    recs: Dict[str, Dict[str, str]] = {}
    n = len(df)
    for col in df.columns:
        ser = df[col]
        dtype = ser.dtype
        # Objects/strings: consider categories
        if ptypes.is_object_dtype(dtype) or ptypes.is_string_dtype(dtype):
            nunique = ser.nunique(dropna=True)
            unique_ratio = nunique / max(1, n)
            if nunique <= 50 or unique_ratio < 0.05:
                recs[col] = {
                    "recommended": "category",
                    "reason": f"{nunique} unique values ({unique_ratio:.2%}); good fit for categorical",
                }
            else:
                recs[col] = {
                    "recommended": "string",
                    "reason": "High cardinality text field; keep as string",
                }
        # Floats: maybe integer-like or downcast floats
        elif ptypes.is_float_dtype(dtype):
            non_na = ser.dropna()
            if non_na.empty:
                recs[col] = {"recommended": "float32", "reason": "All values missing or empty; use float32"}
            else:
                # check integer-like floats
                if (non_na % 1 == 0).all():
                    # determine if fits in 32-bit int
                    minv = int(non_na.min())
                    maxv = int(non_na.max())
                    if -2_147_483_648 <= minv <= maxv <= 2_147_483_647:
                        recs[col] = {
                            "recommended": "int32",
                            "reason": "Float values are integer-like and fit in int32",
                        }
                    else:
                        recs[col] = {"recommended": "int64", "reason": "Integer-like but larger than int32 range"}
                else:
                    recs[col] = {"recommended": "float32", "reason": "Float column — downcast to float32 to save memory"}
        # Integers: consider smaller integer dtype
        elif ptypes.is_integer_dtype(dtype):
            minv = int(df[col].min(skipna=True)) if not df[col].dropna().empty else 0
            maxv = int(df[col].max(skipna=True)) if not df[col].dropna().empty else 0
            if -2_147_483_648 <= minv <= maxv <= 2_147_483_647:
                recs[col] = {"recommended": "int32", "reason": "Fits in int32; downcast from int64"}
            else:
                recs[col] = {"recommended": "int64", "reason": "Requires int64 range"}
        else:
            # fallback: leave as-is
            recs[col] = {"recommended": str(dtype), "reason": "No change recommended"}
    return recs


def apply_dtypes(df: DataFrame, mapping: Dict[str, Dict[str, str]]) -> DataFrame:
    """Apply dtype mapping to `df`.

    `mapping` is column -> {"recommended": dtype_name, "reason": ...}
    Supported targets: 'category', 'string', 'int32', 'int64', 'float32'.
    Returns modified DataFrame.
    """
    df = df.copy()
    for col, info in mapping.items():
        target = info.get("recommended")
        if col not in df.columns:
            LOG.warning("Column %s not in dataframe, skipping dtype application", col)
            continue
        try:
            if target == "category":
                df[col] = df[col].astype("category")
            elif target == "string":
                df[col] = df[col].astype("string")
            elif target == "int32":
                # use pandas nullable integer to allow NaNs
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int32")
            elif target == "int64":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            elif target == "float32":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Float32")
            else:
                LOG.info("No handler for target dtype '%s' for column %s; leaving as-is", target, col)
        except Exception as exc:  # pragma: no cover - defensive
            LOG.error("Failed to convert column %s to %s: %s", col, target, exc)
    return df


def summarize_numeric(df: DataFrame, col: str) -> Dict[str, Any]:
    """Return numeric summary for `col` without mutating `df`.

    If the column is non-numeric, a local conversion with
    `pd.to_numeric(..., errors='coerce')` is used for summary only and
    `converted_for_summary` is set to True.
    """
    if col not in df.columns:
        return {"missing": True}
    ser = df[col]
    converted = False
    if not ptypes.is_numeric_dtype(ser.dtype):
        s = pd.to_numeric(ser, errors="coerce")
        converted = True
    else:
        s = ser
    s_num = s.dropna()
    missing_count = int(ser.isna().sum())
    if s_num.empty:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "missing_count": missing_count,
            "converted_for_summary": converted,
        }
    return {
        "min": float(s_num.min()),
        "max": float(s_num.max()),
        "mean": float(s_num.mean()),
        "median": float(s_num.median()),
        "missing_count": missing_count,
        "converted_for_summary": converted,
    }


def compute_conversion_metrics(
    df_before: DataFrame, df_after: DataFrame, changed_columns: List[str]
) -> Dict[str, Dict[str, Optional[float]]]:
    """Compute conversion/coercion metrics for changed columns.

    Returns mapping column -> metrics dict with keys:
      - coerced_to_nan (int)
      - before_min/before_max/after_min/after_max (float|None)
    Non-numeric min/max are returned as None.
    """
    metrics: Dict[str, Dict[str, Optional[float]]] = {}
    for col in changed_columns:
        before_isna = int(df_before[col].isna().sum()) if col in df_before.columns else 0
        after_isna = int(df_after[col].isna().sum()) if col in df_after.columns else 0
        coerced_to_nan = max(0, after_isna - before_isna)

        def min_max_from_series(ser: pd.Series) -> (Optional[float], Optional[float]):
            s = pd.to_numeric(ser, errors="coerce").dropna()
            if s.empty:
                return (None, None)
            return (float(s.min()), float(s.max()))

        before_min, before_max = min_max_from_series(df_before[col]) if col in df_before.columns else (None, None)
        after_min, after_max = min_max_from_series(df_after[col]) if col in df_after.columns else (None, None)

        metrics[col] = {
            "coerced_to_nan": int(coerced_to_nan),
            "before_min": before_min,
            "before_max": before_max,
            "after_min": after_min,
            "after_max": after_max,
        }
    return metrics


def export_json_sample(df: DataFrame, path: Path, n: int = 20) -> None:
    """Export a deterministic top-`n` sample (head) of `df` to JSON.

    Writes JSON records (list of dicts) with `ensure_ascii=False` and
    `indent=2`. Overwrites silently if file exists.
    """
    LOG.info("Exporting JSON sample (n=%d) to %s", n, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = df.head(n)
    records = rows.to_dict(orient="records")
    with path.open("w", encoding="utf8") as fh:
        json.dump(records, fh, indent=2, ensure_ascii=False)


def export_csv(df: DataFrame, path: Path) -> None:
    LOG.info("Exporting CSV to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def md_table(headers: List[str], rows: List[List[str]], align: List[str]) -> str:
    """Build a GitHub-flavored Markdown table string with alignment.

    align values: 'left', 'center', 'right'.
    """
    if not headers:
        return ""
    # Header
    header_line = "| " + " | ".join(headers) + " |"
    # Alignment row
    align_map = {"left": ":---", "center": ":---:", "right": "---:"}
    align_row = "| " + " | ".join(align_map.get(a, ":---") for a in align) + " |"
    body_lines = []
    for r in rows:
        # Ensure row has same length as headers
        cells = [str(c) for c in r]
        body_lines.append("| " + " | ".join(cells) + " |")
    return "\n".join([header_line, align_row] + body_lines)


def write_markdown_report(info: Dict[str, Any], path: Path) -> None:
    """Write a short markdown summary of the inspection and actions taken."""
    LOG.info("Writing report to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append(f"# Session 1 — Ingest and Schema Report\n")
    lines.append("## Summary\n")
    lines.append(f"- Rows: {info.get('rows')}\n")
    lines.append(f"- Columns: {info.get('columns')}\n")

    # 1) Column dtypes and missing
    lines.append("## Column dtypes and missing values\n")
    dtypes = info.get("dtypes", {})
    missing = info.get("missing", {})
    rows_table: List[List[str]] = []
    for col in dtypes:
        miss = missing.get(col, 0)
        rows_table.append([col, dtypes[col], f"{miss:,}"])
    lines.append("")
    lines.append(md_table(["Column", "Dtype", "Missing"], rows_table, ["left", "left", "right"]))
    lines.append("")

    # 2) Recommended dtype changes
    lines.append("## Recommended dtype changes\n")
    recs = info.get("recommended", {})
    if not recs:
        lines.append("No recommendations.\n")
    else:
        rec_rows: List[List[str]] = []
        for col, r in recs.items():
            rec_rows.append([col, r.get("recommended", ""), r.get("reason", "")])
        lines.append("")
        lines.append(md_table(["Column", "Recommended", "Reason"], rec_rows, ["left", "left", "left"]))
        lines.append("")

    # 3) Changes applied
    lines.append("## Changes applied\n")
    applied = info.get("applied", {})
    if not applied:
        lines.append("No changes applied.\n")
    else:
        app_rows: List[List[str]] = []
        for col, new in applied.items():
            app_rows.append([col, new])
        lines.append("")
        lines.append(md_table(["Column", "Applied Dtype"], app_rows, ["left", "left"]))
        lines.append("")

    # 4) Age and Income summary
    lines.append("## Age and Income\n")
    numeric_summary = info.get("numeric_summary", {})
    if not numeric_summary:
        lines.append("Age/Income columns not present.\n")
    else:
        ai_rows: List[List[str]] = []
        converted_notes: List[str] = []
        for col in ("age", "income"):
            s = numeric_summary.get(col)
            if s is None or s.get("missing"):
                ai_rows.append([col, "—", "—", "—", "—", "—"])
                continue
            minv = s.get("min")
            maxv = s.get("max")
            meanv = s.get("mean")
            medianv = s.get("median")
            missingc = s.get("missing_count", 0)
            converted = s.get("converted_for_summary", False)
            def fmt_num(v, prec=2):
                return f"{v:,.{prec}f}" if isinstance(v, float) else "—"
            ai_rows.append([col, fmt_num(minv, 2), fmt_num(maxv, 2), fmt_num(meanv, 2), fmt_num(medianv, 2), f"{missingc:,}"])
            if converted:
                converted_notes.append(col)
        lines.append("")
        lines.append(md_table(["Column", "Min", "Max", "Mean", "Median", "Missing"], ai_rows, ["left", "right", "right", "right", "right", "right"]))
        lines.append("")
        if converted_notes:
            lines.append("Values converted to numeric for summary only for: " + ", ".join(converted_notes) + ".\n")

    # 5) Conversion metrics
    lines.append("## Conversion Metrics\n")
    conv = info.get("conversion_metrics", {})
    if not conv:
        lines.append("No conversion metrics; no dtype changes applied.\n")
    else:
        cm_rows: List[List[str]] = []
        for col, m in conv.items():
            coerced = int(m.get("coerced_to_nan", 0))
            def maybe_fmt(v):
                return f"{v:.2f}" if isinstance(v, float) else "—"
            cm_rows.append([col, f"{coerced:,}", maybe_fmt(m.get("before_min")), maybe_fmt(m.get("before_max")), maybe_fmt(m.get("after_min")), maybe_fmt(m.get("after_max"))])
        lines.append("")
        lines.append(md_table(["Column", "Coerced to NaN", "Before Min", "Before Max", "After Min", "After Max"], cm_rows, ["left", "right", "right", "right", "right", "right"]))
        lines.append("")

    # Recommended changes before detailed analysis
    lines.append("## Recommended changes before detailed analysis\n")
    if recs:
        for col, r in recs.items():
            lines.append(f"- {col}: {r.get('recommended')} — {r.get('reason')}")
    coerced_warnings = []
    for col, m in conv.items():
        if m.get("coerced_to_nan", 0) > 0:
            coerced_warnings.append(col)
    if coerced_warnings:
        for c in coerced_warnings:
            lines.append(f"- Investigate non-numeric source values in {c} before relying on numeric analysis.")

    with path.open("w", encoding="utf8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    setup_logging()
    input_path = Path("data/raw/NSMES1988.csv")
    out_json = Path("data/processed/NSMES1988_sample.json")
    out_csv = Path("data/processed/NSMES1988new.csv")
    report_path = Path("reports/session1.md")

    LOG.info("Starting session1 ingest/clean")
    df = load_csv(input_path)

    info: Dict[str, Any] = inspect_schema(df)
    LOG.info("Inspected schema: %s", {"rows": info['rows'], "columns": info['columns']})

    # Numeric summaries for Age and Income (pre-conversion)
    numeric_summary: Dict[str, Optional[Dict[str, Any]]] = {}
    for col in ("age", "income"):
        if col in df.columns:
            numeric_summary[col] = summarize_numeric(df, col)
        else:
            numeric_summary[col] = None
    info["numeric_summary"] = numeric_summary

    # Capture dtypes before conversion
    dtypes_before = df.dtypes.apply(str)
    info["dtypes_before"] = dtypes_before.to_dict()

    recs = recommend_dtypes(df)
    info["recommended"] = recs

    # Apply recommended types
    df_converted = apply_dtypes(df, recs)

    # record applied dtypes
    applied = {col: str(df_converted[col].dtype) for col in df_converted.columns}
    info["applied"] = applied

    # Capture dtypes after conversion and changed columns
    dtypes_after = df_converted.dtypes.apply(str)
    info["dtypes_after"] = dtypes_after.to_dict()
    changed_columns = [c for c in df.columns if dtypes_before[c] != dtypes_after.get(c)]
    info["changed_columns"] = changed_columns

    # Compute conversion/coercion metrics for changed columns
    metrics = compute_conversion_metrics(df, df_converted, changed_columns) if changed_columns else {}
    info["conversion_metrics"] = metrics

    export_json_sample(df_converted, out_json, n=20)
    export_csv(df_converted, out_csv)
    write_markdown_report(info, report_path)

    LOG.info("Session1 complete. Outputs:\n  - %s\n  - %s\n  - %s", out_json, out_csv, report_path)


if __name__ == "__main__":
    main()
