"""
Upload validation engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from typing import Dict, List

import pandas as pd
from openpyxl import load_workbook

from config import (
    SHEET_ICG, SHEET_DMM, SHEET_GPIS_SUPPLY, SHEET_GPIS_DEMAND,
    REQUIRED_SHEETS, DOMAINS, GEOGRAPHIES,
    ICG_COLUMNS, DMM_COLUMNS, GPIS_SUPPLY_COLUMNS, GPIS_DEMAND_COLUMNS,
)


@dataclass
class ValidationReport:
    ok: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sheet_row_counts: Dict[str, int] = field(default_factory=dict)

    def fail(self, msg: str):
        self.ok = False
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)


SHEET_SPECS = {
    SHEET_ICG: ICG_COLUMNS,
    SHEET_DMM: DMM_COLUMNS,
    SHEET_GPIS_SUPPLY: GPIS_SUPPLY_COLUMNS,
    SHEET_GPIS_DEMAND: GPIS_DEMAND_COLUMNS,
}


def _read_sheet(xls_bytes: bytes, sheet: str) -> pd.DataFrame:
    return pd.read_excel(BytesIO(xls_bytes), sheet_name=sheet, engine="openpyxl")


def _normalise_cell(v):
    if isinstance(v, str):
        return v.strip()
    return v


def _validate_columns(df: pd.DataFrame, expected: list, sheet: str, report: ValidationReport) -> pd.DataFrame:
    expected_labels = [label for label, _ in expected]
    missing = [c for c in expected_labels if c not in df.columns]
    if missing:
        report.fail(f"[{sheet}] Missing columns: {', '.join(missing)}")
        return df
    df = df[expected_labels].copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(_normalise_cell)
    return df


def _validate_values(df: pd.DataFrame, expected: list, sheet: str, report: ValidationReport):
    for label, spec in expected:
        series = df[label]
        if isinstance(spec, list):
            allowed = set(spec)
            mask = series.notna() & ~series.isin(allowed)
            if mask.any():
                df.loc[mask, label] = None
        elif spec == "int":
            df[label] = pd.to_numeric(series, errors="coerce")
            neg = df[label] < 0
            if neg.any():
                df.loc[neg, label] = 0
        elif spec == "domain":
            allowed = set(DOMAINS)
            mask = series.notna() & ~series.isin(allowed)
            if mask.any():
                df.loc[mask, label] = None
        elif spec == "geography":
            allowed = set(GEOGRAPHIES)
            mask = series.notna() & ~series.isin(allowed)
            if mask.any():
                df.loc[mask, label] = None


def validate_workbook(xls_bytes: bytes):
    report = ValidationReport()
    dfs: Dict[str, pd.DataFrame] = {}

    try:
        wb = load_workbook(BytesIO(xls_bytes), read_only=True, data_only=True)
        present = set(wb.sheetnames)
    except Exception as e:
        report.fail(f"Could not open workbook: {e}")
        return dfs, report

    missing_sheets = [s for s in REQUIRED_SHEETS if s not in present]
    if missing_sheets:
        report.fail(f"Missing required sheets: {', '.join(missing_sheets)}")
        return dfs, report

    for sheet, spec in SHEET_SPECS.items():
        try:
            df = _read_sheet(xls_bytes, sheet)
        except Exception as e:
            report.fail(f"[{sheet}] Could not read sheet: {e}")
            continue

        df = df.dropna(how="all").reset_index(drop=True)
        df = _validate_columns(df, spec, sheet, report)

        if report.ok:
            _validate_values(df, spec, sheet, report)

        report.sheet_row_counts[sheet] = len(df)
        dfs[sheet] = df

    return dfs, report
