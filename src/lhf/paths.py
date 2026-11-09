"""Filesystem paths for lhf."""
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW = os.path.join(REPO, "data", "raw")
DATA_CURATED = os.path.join(REPO, "data", "curated")
