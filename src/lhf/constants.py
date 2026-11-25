"""Constants reader from data/curated/constants.csv."""
import os
import pandas as pd
from lhf.paths import DATA_CURATED

_CONSTANTS = None


def _load_constants():
    """Load and cache scalar conversion constants from data/curated/constants.csv."""
    global _CONSTANTS
    if _CONSTANTS is None:
        path = os.path.join(DATA_CURATED, "constants.csv")
        df = pd.read_csv(path)
        _CONSTANTS = {str(row["id"]): float(row["value"]) for _, row in df.iterrows()}
    return _CONSTANTS


def get(id_):
    """Return the float constant value for the given constant ID."""
    table = _load_constants()
    if id_ not in table:
        raise KeyError(id_)
    return table[id_]
