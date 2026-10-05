import subprocess
import json
import re
import os
import time
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi

DISHES = [
    ("paneer_butter_masala", "paneer butter masala recipe"),
    ("dal_makhani", "dal makhani recipe"),
    ("chole", "chole chana masala recipe"),
    ("rajma", "rajma recipe"),
    ("aloo_paratha", "aloo paratha recipe"),
    ("samosa", "samosa recipe"),
    ("onion_pakora", "onion pakoda bhajji recipe"),
    ("puri_bhature", "puri bhature recipe"),
    ("pav_bhaji", "pav bhaji recipe"),
    ("butter_chicken", "butter chicken recipe"),
    ("chicken_biryani", "chicken biryani recipe"),
    ("egg_curry", "egg curry recipe"),
    ("gulab_jamun", "gulab jamun recipe"),
    ("gajar_halwa", "gajar ka halwa recipe"),
    ("jalebi", "jalebi recipe"),
    ("poha", "poha recipe"),
    ("masala_dosa", "masala dosa recipe"),
    ("sambar", "sambar recipe"),
    ("kheer", "rice kheer recipe"),
    ("aloo_tikki", "aloo tikki recipe"),
]

LIVER_KEYWORDS = {
    "oil": ["oil", "tel", "refined oil"],
    "ghee": ["ghee", "clarified butter", "desi ghee"],
    "butter": ["butter", "makhan", "makkhan"],
    "cream": ["cream", "malai"],
    "khoya": ["khoya", "mawa"],
    "sugar": ["sugar", "chini", "cheeni", "chasni", "sugar syrup"],
    "jaggery": ["jaggery", "gur", "gud"],
    "maida": ["maida", "all purpose flour"],
    "salt": ["salt", "namak"]
}

def get_top_videos(query, max_vids=3):
    cmd = [
        "yt-dlp",
        f"ytsearch{max_vids}:{query}",
        "--flat-playlist",
        "--dump-json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        videos = []
        for line in res.stdout.strip().split("\n"):
            if line:
                videos.append(json.loads(line))
        return videos
    except Exception as e:
        print(f"Error searching videos for {query}: {e}")
        return []

def get_video_details(video_id):
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--dump-json",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception as e:
        print(f"Error fetching details for {video_id}: {e}")
        return None

def extract_ingredients_from_desc(desc):
    if not desc:
        return []
    lines = desc.split("\n")
    ingr_lines = []
    in_ingr_section = False
    
    for l in lines:
        clean = l.strip()
        if not clean:
            continue
        lower = clean.lower()
        if any(h in lower for h in ["ingredient", "ingredients", "सामग्री", "samagri", "for gravy", "for paste", "for dough"]):
            in_ingr_section = True
            continue
        if in_ingr_section:
            # stop if section ends
            if any(stop in lower for stop in ["step by step", "method", "instructions", "subscribe", "social media", "follow me", "music", "gear", "disclaimer", "official website"]):
                in_ingr_section = False
                continue
            # if contains measurement or liver keyword
            if any(re.search(r'\b' + re.escape(u) + r'\b', lower) for u in ['cup', 'tbsp', 'tsp', 'gm', 'g', 'ml', 'pinch', 'to taste', 'as required', 'spoon', 'katori', 'nos', 'piece']) or any(kw in lower for cat, kws in LIVER_KEYWORDS.items() for kw in kws):
                ingr_lines.append(clean)
    return ingr_lines

def analyze_transcript(video_id):
    try:
        t = YouTubeTranscriptApi()
        trans = t.fetch(video_id, languages=['hi', 'en'])
        snippets = [s.text for s in trans.snippets]
        full_text = " ".join(snippets)
        return True, full_text
    except Exception as e:
        return False, str(e)
