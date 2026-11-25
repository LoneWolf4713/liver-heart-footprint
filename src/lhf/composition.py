import math
import os
import numpy as np
import pandas as pd
from lhf.paths import DATA_RAW, DATA_CURATED
from lhf import constants

_TABLE = None

# pure fats and oils in ifct (T001-T014) have energy computed directly from fat content
OIL_CODES = {f"T{i:03d}" for i in range(1, 12 + 3)}

COLUMNS = [
    "name",
    "source",
    "energy_kj",
    "energy_kcal",
    "fat_g",
    "sfa_g",
    "mufa_g",
    "pufa_g",
    "tfa_g",
    "carb_g",
    "freesugar_g",
    "fibre_g",
    "protein_g",
    "sodium_mg",
    "water_g",
    "energy_flag",
]

NUTRIENT_COLUMNS = (
    "energy_kj",
    "energy_kcal",
    "fat_g",
    "sfa_g",
    "mufa_g",
    "pufa_g",
    "tfa_g",
    "carb_g",
    "freesugar_g",
    "fibre_g",
    "protein_g",
    "sodium_mg",
    "water_g",
)


def _to_num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


# leave missing values as nan so missing tfa or water doesn't turn into 0
def _to_nan_or(series):
    return pd.to_numeric(series, errors="coerce")


# merge ifct 2017, indb uk/us tables, and curated indian product rows
def _build_table():
    kj_per_kcal = constants.get("KJ_PER_KCAL")
    fat_kj_per_g = constants.get("FAT_KJ_PER_G")
    fat_kcal_per_g = constants.get("FAT_KCAL_PER_G")

    # ifct 2017 main table
    ifct_path = os.path.join(DATA_RAW, "ifct2017_transcription", "ifct2017_compositions.csv")
    ifct_raw = pd.read_csv(ifct_path)
    oil = ifct_raw["code"].astype(str).isin(OIL_CODES)
    fat = _to_num(ifct_raw["fatce"])
    enerc = _to_num(ifct_raw["enerc"])

    ifct_df = pd.DataFrame(
        {
            "code": ifct_raw["code"].astype(str),
            "name": ifct_raw["name"].astype(str),
            "source": "IFCT2017",
            "energy_kj": np.where(oil, fat * fat_kj_per_g, enerc),
            "energy_kcal": np.where(oil, fat * fat_kcal_per_g, enerc / kj_per_kcal),
            "fat_g": fat,
            "sfa_g": _to_num(ifct_raw["fasat"]),
            "mufa_g": _to_num(ifct_raw["fams"]),
            "pufa_g": _to_num(ifct_raw["fapu"]),
            "tfa_g": _to_nan_or(ifct_raw["fatrn"]),
            "carb_g": _to_num(ifct_raw["choavldf"]),
            "freesugar_g": _to_num(ifct_raw["fsugar"]),
            "fibre_g": _to_num(ifct_raw["fibtg"]),
            "protein_g": _to_num(ifct_raw["protcnt"]),
            "sodium_mg": _to_num(ifct_raw["na"]) * 1000,
            "water_g": _to_nan_or(ifct_raw["water"]),
            "energy_flag": np.where(oil, "FAT_ENERGY_DERIVED", ""),
        }
    )

    # indb uk and us tables (fatty acids are stored in mg here, convert to g)
    indb_dfs = []
    indb_sources = [("UK_fct.xlsx", "INDB_UK"), ("US_fct.xlsx", "INDB_US")]
    for filename, source_name in indb_sources:
        raw_path = os.path.join(DATA_RAW, "indb", filename)
        raw_df = pd.read_excel(raw_path, sheet_name="Sheet1")
        raw_df = raw_df[raw_df["food_code"].notna()]
        df = pd.DataFrame(
            {
                "code": raw_df["food_code"].astype(str),
                "name": raw_df["food_name"].astype(str),
                "source": source_name,
                "energy_kj": _to_num(raw_df["energy_kj"]),
                "energy_kcal": _to_num(raw_df["energy_kcal"]),
                "fat_g": _to_num(raw_df["fat_g"]),
                "sfa_g": _to_num(raw_df["sfa_mg"]) / 1000,
                "mufa_g": _to_num(raw_df["mufa_mg"]) / 1000,
                "pufa_g": _to_num(raw_df["pufa_mg"]) / 1000,
                "tfa_g": np.nan,
                "carb_g": _to_num(raw_df["carb_g"]),
                "freesugar_g": _to_num(raw_df["freesugar_g"]),
                "fibre_g": _to_num(raw_df["fibre_g"]),
                "protein_g": _to_num(raw_df["protein_g"]),
                "sodium_mg": _to_num(raw_df["sodium_mg"]),
                "water_g": np.nan,
                "energy_flag": "",
            }
        )
        indb_dfs.append(df)

    # indian dairy and packaged rows
    inp_path = os.path.join(DATA_CURATED, "indian_products.csv")
    inp_raw = pd.read_csv(inp_path)
    inp_df = pd.DataFrame(
        {
            "code": inp_raw["code"].astype(str),
            "name": inp_raw["name"].astype(str),
            "source": "IN_LABEL",
            "energy_kj": _to_num(inp_raw["energy_kj"]),
            "energy_kcal": _to_num(inp_raw["energy_kcal"]),
            "fat_g": _to_num(inp_raw["fat_g"]),
            "sfa_g": _to_num(inp_raw["sfa_g"]),
            "mufa_g": _to_num(inp_raw["mufa_g"]),
            "pufa_g": _to_num(inp_raw["pufa_g"]),
            "tfa_g": _to_nan_or(inp_raw["tfa_g"]),
            "carb_g": _to_num(inp_raw["carb_g"]),
            "freesugar_g": _to_num(inp_raw["freesugar_g"]),
            "fibre_g": _to_num(inp_raw["fibre_g"]),
            "protein_g": _to_num(inp_raw["protein_g"]),
            "sodium_mg": _to_num(inp_raw["sodium_mg"]),
            "water_g": _to_nan_or(inp_raw["water_g"]),
            "energy_flag": inp_raw["energy_flag"].fillna(""),
        }
    )

    combined = pd.concat([ifct_df, indb_dfs[0], indb_dfs[1], inp_df], ignore_index=True)
    combined = combined.set_index("code")
    return combined[COLUMNS]


def _get_table():
    global _TABLE
    if _TABLE is None:
        _TABLE = _build_table()
    return _TABLE


def load_table():
    return _get_table().copy()


def get(code):
    table = _get_table()
    code_str = str(code)
    if code_str not in table.index:
        raise KeyError(code)
    row = table.loc[code_str].to_dict()
    row["code"] = code_str
    return row


def nutrients_for(code, grams):
    table = _get_table()
    code_str = str(code)
    if code_str not in table.index:
        raise KeyError(code)
    if grams is None or isinstance(grams, bool):
        raise ValueError("grams cannot be None or boolean")
    try:
        g = float(grams)
    except (TypeError, ValueError) as err:
        raise ValueError(f"grams must be numeric, got {grams!r}") from err
    if math.isnan(g) or not math.isfinite(g) or g < 0:
        raise ValueError(f"grams must be non-negative finite number, got {grams!r}")
    row = table.loc[code_str]
    factor = g / 100
    return {col: float(row[col]) * factor for col in NUTRIENT_COLUMNS}
