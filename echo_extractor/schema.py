"""Pydantic model for the structured API response and xlsx column mapping."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class EchoData(BaseModel):
    """All extractable fields from an Adult Echo Report.

    Field names use snake_case Python identifiers; the COLUMN_MAP below
    translates each to its exact xlsx column name(s).
    All fields default to None — a None value writes a truly blank xlsx cell.
    """

    # Patient Information
    age: Optional[float] = None
    agestring: Optional[str] = None
    sex: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bsa: Optional[float] = None
    savedate: Optional[str] = None
    indication: Optional[str] = None

    # Teichholz
    ivsd: Optional[float] = None
    lvidd: Optional[float] = None
    lvpwd: Optional[float] = None
    lvids: Optional[float] = None
    ivss: Optional[float] = None
    lvpws: Optional[float] = None
    edv: Optional[float] = None
    esv: Optional[float] = None
    ef: Optional[float] = None
    fs: Optional[float] = None
    sv: Optional[float] = None
    si: Optional[float] = None

    # Mitral Valve
    mv_e: Optional[float] = None
    mv_a: Optional[float] = None
    mv_dt: Optional[float] = None
    e_a: Optional[float] = None
    mv_pht: Optional[float] = None
    dec_slope: Optional[float] = None
    mva_pht: Optional[float] = None
    mv_vmax: Optional[float] = None
    mv_vmean: Optional[float] = None
    mv_vti: Optional[float] = None
    mv_pgmax: Optional[float] = None
    mv_pgmean: Optional[float] = None

    # Aortic Valve
    av_vmax: Optional[float] = None
    av_pgmax: Optional[float] = None
    av_vmean: Optional[float] = None
    av_pgmean: Optional[float] = None
    av_vti: Optional[float] = None

    # LVOT
    lvot_diam: Optional[float] = None
    lvot_vmax: Optional[float] = None
    lvot_vmean: Optional[float] = None
    lvot_pgmax: Optional[float] = None
    lvot_pgmean: Optional[float] = None
    lvot_vti: Optional[float] = None

    # Pulmonary Valve
    pv_vmax: Optional[float] = None
    pv_pgmax: Optional[float] = None
    pv_vmean: Optional[float] = None
    pv_pgmean: Optional[float] = None
    pv_vti: Optional[float] = None
    pv_acc_time: Optional[float] = None

    # TR
    tr_vmax: Optional[float] = None
    tr_pgmax: Optional[float] = None
    tr_vmean: Optional[float] = None
    tr_pgmean: Optional[float] = None
    tr_vti: Optional[float] = None
    rap: Optional[float] = None
    rsvp: Optional[float] = None

    # MR
    mr_vmax: Optional[float] = None
    mr_pgmax: Optional[float] = None
    mr_vti: Optional[float] = None

    # AR / AI
    ar_vmax: Optional[float] = None
    ar_pgmax: Optional[float] = None
    ar_dt: Optional[float] = None
    ai_pht: Optional[float] = None
    ai_dec_slope: Optional[float] = None

    # AO / LA (M-mode)
    aod: Optional[float] = None
    las_diam: Optional[float] = None
    aod_las: Optional[float] = None

    # RV / LV M-mode
    tapse: Optional[float] = None
    mapse: Optional[float] = None

    # TDI
    ea_l: Optional[float] = None
    ea_m: Optional[float] = None
    aa_l: Optional[float] = None
    aa_m: Optional[float] = None
    sa_l: Optional[float] = None
    sa_m: Optional[float] = None


# Maps each EchoData field → one or more xlsx column names.
# A list means the same value is written to multiple columns.
COLUMN_MAP: dict[str, str | list[str]] = {
    "age": "Age",
    "agestring": "agestring",
    "sex": "sex",
    "height": ["height", "hoheight"],
    "weight": ["weight", "weightkg", "howeight"],
    "bsa": "bsa",
    "savedate": ["savedate", "visit_date", "formatsavedate"],
    "indication": "indication",
    "ivsd": "IVSd",
    "lvidd": "LVIDd",
    "lvpwd": "LVPWd",
    "lvids": "LVIDs",
    "ivss": "IVSs",
    "lvpws": "LVPWs",
    "edv": "EDV",
    "esv": "ESV",
    "ef": "EF",
    "fs": "FS",
    "sv": "SV",
    "si": "SI",
    "mv_e": "MV E pt",
    "mv_a": "MV A pt",
    "mv_dt": "MV DT",
    "e_a": "E/A",
    "mv_pht": "MV PHT",
    "dec_slope": "Dec Slope",
    "mva_pht": "MVA(PHT)",
    "mv_vmax": "MV Vmax",
    "mv_vmean": "MV Vmean",
    "mv_vti": "MV VTI",
    "mv_pgmax": "MV Pgmax",
    "mv_pgmean": "MV Pgmean",
    "av_vmax": "av vmax",
    "av_pgmax": "AV Pgmax",
    "av_vmean": "Av Vmean",
    "av_pgmean": "AV Pgmean",
    "av_vti": "AV VTI",
    "lvot_diam": "LVOT diam",
    "lvot_vmax": "LVOT Vmax",
    "lvot_vmean": "LVOT Vmean",
    "lvot_pgmax": "lvot pgmax",
    "lvot_pgmean": "lvomean",
    "lvot_vti": "LVOT VTI",
    "pv_vmax": "PV Vmax",
    "pv_pgmax": "PV Pgmax",
    "pv_vmean": "PV Vmean",
    "pv_pgmean": "PV Pgmean",
    "pv_vti": "PV VTI",
    "pv_acc_time": "PV Acc Time",
    "tr_vmax": "tr vmax",
    "tr_pgmax": "TR Pgmax",
    "tr_vmean": "TR Vmean",
    "tr_pgmean": "TR Pgmean",
    "tr_vti": "TR VTI",
    "rap": "RAP",
    "rsvp": "RSVP",
    "mr_vmax": "MR Vmax",
    "mr_pgmax": "MR Pgmax",
    "mr_vti": "MR VTI",
    "ar_vmax": "AR Vmax",
    "ar_pgmax": "AR Pgmax",
    "ar_dt": "AR DT",
    "ai_pht": "AI PHT",
    "ai_dec_slope": "AI Dec slope",
    "aod": "Aod",
    "las_diam": "Las diam",
    "aod_las": "Aod/Las",
    "tapse": "TAPSE",
    "mapse": "MAPSE",
    "ea_l": "Ea(l)",
    "ea_m": "Ea(m)",
    "aa_l": "Aa(l)",
    "aa_m": "Aa(m)",
    "sa_l": "Sa(l)",
    "sa_m": "Sa(m)",
}

# Xlsx columns that must NEVER be written regardless of what is found in images.
ALWAYS_BLANK: frozenset[str] = frozenset({
    "Patient ID", "patientid", "id", "unique_id", "exam_id",
    "Las/Aod", "RWT", "LV Mass", "LV Mass-c", "LV Mass-i",
    "A/E", "E/Ea(l)", "E/Ea(m)", "Ea/Aa(l)", "Ea/Aa(m)", "lvot/av vti",
    "Unnamed: 49", "unnamed: 0", "version",
    "weightlb", "weightoz",
})

EXTRACTION_PROMPT = """You are an expert echocardiography data extractor. You have been given {n_pages} pages of an Adult Echo Report as images.

Extract ALL measurements visible across all pages and return them as a single JSON object.

CRITICAL RULES:
1. Return ONLY valid JSON — no markdown fences, no preamble, no explanation
2. Use null for any field not present in the report — never substitute 0, "N/A", "--", or ""
3. Treat "--", blank cells, or dashes in the report as null
4. Strip units from numeric values: store 12.90 not "12.90 mm"
5. For dates use ISO format YYYY-MM-DD (e.g. "2025-04-02")
6. For sex: "M" for Male, "F" for Female
7. For age (numeric): extract just the number (e.g. 65 from "65Years")
8. For agestring: extract the full string (e.g. "65Years")
9. Look carefully at ALL {n_pages} pages — measurements are spread across multiple pages

The JSON must have exactly these keys:

{schema_json}

Extraction guide — report label → JSON key:

PATIENT INFORMATION section:
  Age (numeric only)  → age
  Age (full string)   → agestring
  Gender              → sex
  Height (cm)         → height
  Weight (kg)         → weight
  BSA                 → bsa
  Study Date          → savedate  (YYYY-MM-DD)
  Indications         → indication (free text)

TEICHHOLZ section:
  IVSd  → ivsd    LVIDd → lvidd   LVPWd → lvpwd
  LVIDs → lvids   IVSs  → ivss    LVPWs → lvpws
  EDV   → edv     ESV   → esv     EF    → ef
  FS    → fs      SV    → sv      SI    → si

MITRAL VALVE section:
  MV Peak E vel  → mv_e       MV Peak A vel  → mv_a
  MV Decel Time  → mv_dt      E/A            → e_a
  MV PHT         → mv_pht     MV Decel Slope → dec_slope
  MVA (PHT)      → mva_pht    MV Vmax        → mv_vmax
  MV Vmean       → mv_vmean   MV VTI         → mv_vti
  MV PGmax       → mv_pgmax   MV PGmean      → mv_pgmean

AORTIC VALVE section:
  AV Vmax   → av_vmax    AV PGmax  → av_pgmax
  AV Vmean  → av_vmean   AV PGmean → av_pgmean
  AV VTI    → av_vti

LVOT section:
  LVOT diam   → lvot_diam    LVOT Vmax   → lvot_vmax
  LVOT Vmean  → lvot_vmean   LVOT PGmax  → lvot_pgmax
  LVOT PGmean → lvot_pgmean  LVOT VTI    → lvot_vti

PULMONARY VALVE section:
  PV Vmax    → pv_vmax     PV PGmax   → pv_pgmax
  PV Vmean   → pv_vmean    PV PGmean  → pv_pgmean
  PV VTI     → pv_vti      PV Acc Time → pv_acc_time

TR section:
  TR Vmax   → tr_vmax     TR PGmax   → tr_pgmax
  TR Vmean  → tr_vmean    TR PGmean  → tr_pgmean
  TR VTI    → tr_vti      RAP select → rap
  RVSP      → rsvp

MR section:
  MR Vmax → mr_vmax   MR PGmax → mr_pgmax   MR VTI → mr_vti

AR / AI section:
  AR Vmax      → ar_vmax    AR PGmax    → ar_pgmax
  AR DT        → ar_dt      AI PHT      → ai_pht
  AI Dec slope → ai_dec_slope

AO/LA (M) section:
  AOd      → aod        LAs Diam → las_diam   AOd/LAs → aod_las

RV (M) section:
  TAPSE → tapse

LV (M) section:
  MAPSE → mapse

TDI section:
  Ea(l) → ea_l   Ea(m) → ea_m
  Aa(l) → aa_l   Aa(m) → aa_m
  Sa(l) → sa_l   Sa(m) → sa_m
"""
