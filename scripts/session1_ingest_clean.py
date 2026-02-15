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
from typing import Any, Dict

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


def export_json(df: DataFrame, path: Path) -> None:
    LOG.info("Exporting JSON to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = df.to_dict(orient="records")
    with path.open("w", encoding="utf8") as fh:
        json.dump(records, fh, indent=2, default=str)


def export_csv(df: DataFrame, path: Path) -> None:
    LOG.info("Exporting CSV to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_markdown_report(info: Dict[str, Any], path: Path) -> None:
    """Write a short markdown summary of the inspection and actions taken."""
    LOG.info("Writing report to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(f"# Session 1 — Ingest and Schema Report\n")
    lines.append("## Summary\n")
    lines.append(f"- Rows: {info.get('rows')}\n")
    lines.append(f"- Columns: {info.get('columns')}\n")

    lines.append("## Column dtypes and missing values\n")
    dtypes = info.get("dtypes", {})
    missing = info.get("missing", {})
    lines.append("| Column | Dtype | Missing |")
    lines.append("|---|---:|---:|")
    for col in dtypes:
        lines.append(f"| {col} | {dtypes[col]} | {missing.get(col, 0)} |")

    lines.append("\n## Recommended dtype changes\n")
    recs = info.get("recommended", {})
    if recs:
        lines.append("| Column | Recommended | Reason |")
        lines.append("|---|---|---|")
        for col, r in recs.items():
            lines.append(f"| {col} | {r.get('recommended')} | {r.get('reason')} |")
    else:
        lines.append("No recommendations generated.")

    lines.append("\n## Changes applied\n")
    applied = info.get("applied", {})
    if applied:
        for col, new in applied.items():
            lines.append(f"- {col}: set to {new}")
    else:
        lines.append("- No changes applied.")

    with path.open("w", encoding="utf8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    setup_logging()
    input_path = Path("data/raw/NSMES1988.csv")
    out_json = Path("data/processed/NSMES1988.json")
    out_csv = Path("data/processed/NSMES1988new.csv")
    report_path = Path("reports/session1.md")

    LOG.info("Starting session1 ingest/clean")
    df = load_csv(input_path)

    info: Dict[str, Any] = inspect_schema(df)
    LOG.info("Inspected schema: %s", {"rows": info['rows'], "columns": info['columns']})

    recs = recommend_dtypes(df)
    info["recommended"] = recs

    # Apply recommended types
    df_converted = apply_dtypes(df, recs)

    # record applied dtypes
    applied = {col: str(df_converted[col].dtype) for col in df_converted.columns}
    info["applied"] = applied

    export_json(df_converted, out_json)
    export_csv(df_converted, out_csv)
    write_markdown_report(info, report_path)

    LOG.info("Session1 complete. Outputs:\n  - %s\n  - %s\n  - %s", out_json, out_csv, report_path)


if __name__ == "__main__":
    main()
