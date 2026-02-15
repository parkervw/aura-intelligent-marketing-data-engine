# Session 1 — Ingest and Schema Report

## Summary

- Rows: 4406

- Columns: 19

## Column dtypes and missing values

| Column | Dtype | Missing |
|---|---:|---:|
| Unnamed: 0 | int64 | 0 |
| visits | int64 | 0 |
| nvisits | int64 | 0 |
| ovisits | int64 | 0 |
| novisits | int64 | 0 |
| emergency | int64 | 0 |
| hospital | int64 | 0 |
| health | str | 0 |
| chronic | int64 | 0 |
| adl | str | 0 |
| region | str | 0 |
| age | float64 | 0 |
| gender | str | 0 |
| married | str | 0 |
| school | int64 | 0 |
| income | float64 | 0 |
| employed | str | 0 |
| insurance | str | 0 |
| medicaid | str | 0 |

## Recommended dtype changes

| Column | Recommended | Reason |
|---|---|---|
| Unnamed: 0 | int32 | Fits in int32; downcast from int64 |
| visits | int32 | Fits in int32; downcast from int64 |
| nvisits | int32 | Fits in int32; downcast from int64 |
| ovisits | int32 | Fits in int32; downcast from int64 |
| novisits | int32 | Fits in int32; downcast from int64 |
| emergency | int32 | Fits in int32; downcast from int64 |
| hospital | int32 | Fits in int32; downcast from int64 |
| health | category | 3 unique values (0.07%); good fit for categorical |
| chronic | int32 | Fits in int32; downcast from int64 |
| adl | category | 2 unique values (0.05%); good fit for categorical |
| region | category | 4 unique values (0.09%); good fit for categorical |
| age | float32 | Float column — downcast to float32 to save memory |
| gender | category | 2 unique values (0.05%); good fit for categorical |
| married | category | 2 unique values (0.05%); good fit for categorical |
| school | int32 | Fits in int32; downcast from int64 |
| income | float32 | Float column — downcast to float32 to save memory |
| employed | category | 2 unique values (0.05%); good fit for categorical |
| insurance | category | 2 unique values (0.05%); good fit for categorical |
| medicaid | category | 2 unique values (0.05%); good fit for categorical |

## Changes applied

- Unnamed: 0: set to Int32
- visits: set to Int32
- nvisits: set to Int32
- ovisits: set to Int32
- novisits: set to Int32
- emergency: set to Int32
- hospital: set to Int32
- health: set to category
- chronic: set to Int32
- adl: set to category
- region: set to category
- age: set to Float32
- gender: set to category
- married: set to category
- school: set to Int32
- income: set to Float32
- employed: set to category
- insurance: set to category
- medicaid: set to category

## Age and Income

| Column | Min | Max | Mean | Median | Missing | Converted for summary |
|---|---:|---:|---:|---:|---:|---:|
| age | 6.600 | 10.900 | 7.402 | 7.300 | 0 | False |
| income | -1.012 | 54.835 | 2.527 | 1.698 | 0 | False |

## Conversion Metrics

| Column | coerced_to_nan | before_min | before_max | after_min | after_max |
|---|---:|---:|---:|---:|---:|
| Unnamed: 0 | 0 | 1.000 | 4406.000 | 1.000 | 4406.000 |
| visits | 0 | 0.000 | 89.000 | 0.000 | 89.000 |
| nvisits | 0 | 0.000 | 104.000 | 0.000 | 104.000 |
| ovisits | 0 | 0.000 | 141.000 | 0.000 | 141.000 |
| novisits | 0 | 0.000 | 155.000 | 0.000 | 155.000 |
| emergency | 0 | 0.000 | 12.000 | 0.000 | 12.000 |
| hospital | 0 | 0.000 | 8.000 | 0.000 | 8.000 |
| health | 0 | — | — | — | — |
| chronic | 0 | 0.000 | 8.000 | 0.000 | 8.000 |
| adl | 0 | — | — | — | — |
| region | 0 | — | — | — | — |
| age | 0 | 6.600 | 10.900 | 6.600 | 10.900 |
| gender | 0 | — | — | — | — |
| married | 0 | — | — | — | — |
| school | 0 | 0.000 | 18.000 | 0.000 | 18.000 |
| income | 0 | -1.012 | 54.835 | -1.013 | 54.835 |
| employed | 0 | — | — | — | — |
| insurance | 0 | — | — | — | — |
| medicaid | 0 | — | — | — | — |

## Recommended changes before detailed analysis

- Unnamed: 0: int32 — Fits in int32; downcast from int64
- visits: int32 — Fits in int32; downcast from int64
- nvisits: int32 — Fits in int32; downcast from int64
- ovisits: int32 — Fits in int32; downcast from int64
- novisits: int32 — Fits in int32; downcast from int64
- emergency: int32 — Fits in int32; downcast from int64
- hospital: int32 — Fits in int32; downcast from int64
- health: category — 3 unique values (0.07%); good fit for categorical
- chronic: int32 — Fits in int32; downcast from int64
- adl: category — 2 unique values (0.05%); good fit for categorical
- region: category — 4 unique values (0.09%); good fit for categorical
- age: float32 — Float column — downcast to float32 to save memory
- gender: category — 2 unique values (0.05%); good fit for categorical
- married: category — 2 unique values (0.05%); good fit for categorical
- school: int32 — Fits in int32; downcast from int64
- income: float32 — Float column — downcast to float32 to save memory
- employed: category — 2 unique values (0.05%); good fit for categorical
- insurance: category — 2 unique values (0.05%); good fit for categorical
- medicaid: category — 2 unique values (0.05%); good fit for categorical