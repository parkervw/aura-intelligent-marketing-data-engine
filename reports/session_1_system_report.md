# Session 1 — Ingest and Schema Report

## Summary

- Rows: 4406

- Columns: 19

## Column dtypes and missing values


| Column | Dtype | Missing |
| :--- | :--- | ---: |
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
| :--- | :--- | :--- |
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


| Column | Applied Dtype |
| :--- | :--- |
| Unnamed: 0 | Int32 |
| visits | Int32 |
| nvisits | Int32 |
| ovisits | Int32 |
| novisits | Int32 |
| emergency | Int32 |
| hospital | Int32 |
| health | category |
| chronic | Int32 |
| adl | category |
| region | category |
| age | Float32 |
| gender | category |
| married | category |
| school | Int32 |
| income | Float32 |
| employed | category |
| insurance | category |
| medicaid | category |

## Age and Income


| Column | Min | Max | Mean | Median | Missing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| age | 6.60 | 10.90 | 7.40 | 7.30 | 0 |
| income | -1.01 | 54.84 | 2.53 | 1.70 | 0 |

## Conversion Metrics


| Column | Coerced to NaN | Before Min | Before Max | After Min | After Max |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Unnamed: 0 | 0 | 1.00 | 4406.00 | 1.00 | 4406.00 |
| visits | 0 | 0.00 | 89.00 | 0.00 | 89.00 |
| nvisits | 0 | 0.00 | 104.00 | 0.00 | 104.00 |
| ovisits | 0 | 0.00 | 141.00 | 0.00 | 141.00 |
| novisits | 0 | 0.00 | 155.00 | 0.00 | 155.00 |
| emergency | 0 | 0.00 | 12.00 | 0.00 | 12.00 |
| hospital | 0 | 0.00 | 8.00 | 0.00 | 8.00 |
| health | 0 | — | — | — | — |
| chronic | 0 | 0.00 | 8.00 | 0.00 | 8.00 |
| adl | 0 | — | — | — | — |
| region | 0 | — | — | — | — |
| age | 0 | 6.60 | 10.90 | 6.60 | 10.90 |
| gender | 0 | — | — | — | — |
| married | 0 | — | — | — | — |
| school | 0 | 0.00 | 18.00 | 0.00 | 18.00 |
| income | 0 | -1.01 | 54.84 | -1.01 | 54.84 |
| employed | 0 | — | — | — | — |
| insurance | 0 | — | — | — | — |
| medicaid | 0 | — | — | — | — |
