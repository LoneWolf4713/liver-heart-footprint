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

DEEP_FRIED_DISHES = ["samosa", "onion_pakora", "puri_bhature", "jalebi", "gulab_jamun", "aloo_tikki"]

LIVER_KEYWORDS = {
    "oil": ["oil", "tel", "refined oil", "cooking oil"],
    "ghee": ["ghee", "clarified butter", "desi ghee"],
    "butter": ["butter", "makhan", "makkhan"],
    "cream": ["cream", "malai"],
    "khoya": ["khoya", "mawa"],
    "sugar": ["sugar", "chini", "cheeni", "chasni", "sugar syrup"],
    "jaggery": ["jaggery", "gur", "gud"],
    "maida": ["maida", "all purpose flour"],
    "salt": ["salt", "namak"]
}

VAGUE_PATTERNS = [
    r'\bas required\b', r'\bas needed\b', r'\bto taste\b', r'\bfor frying\b',
    r'\bfor deep frying\b', r'\bdeep frying\b', r'\bswad anusar\b', r'\blittle\b', r'\bthoda\b',
    r'\benough\b', r'\bsome\b', r'\boptional\b', r'\bfew drops\b'
]

RANGE_PATTERNS = [
    r'\d+\s*(?:to|-)\s*\d+',
    r'\d+/\d+\s*(?:to|-)\s*\d+/\d+',
    r'\d+\s*or\s*\d+'
]

EXACT_UNITS = [
    'cup', 'cups', 'tbsp', 'tablespoon', 'tablespoons', 'tsp', 'teaspoon', 'teaspoons',
    'g', 'gm', 'gms', 'gram', 'grams', 'kg', 'kilogram', 'ml', 'katori', 'pinch', 'pinches',
    'karchi', 'ladle', 'spoon', 'spoons'
]

def classify_yt_line(line):
    line_clean = line.strip().lower()
    
    is_liver = False
    liver_cat = None
    for cat, kws in LIVER_KEYWORDS.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', line_clean):
                is_liver = True
                liver_cat = cat
                break
        if is_liver:
            break

    is_vague = any(re.search(p, line_clean) for p in VAGUE_PATTERNS)
    is_range = any(re.search(p, line_clean) for p in RANGE_PATTERNS)
    has_exact_unit = any(re.search(r'\b' + re.escape(u) + r'\b', line_clean) for u in EXACT_UNITS)
    has_number = bool(re.search(r'\d', line_clean) or re.search(r'\b(one|two|three|half|quarter|ek|do|aadha)\b', line_clean))

    if is_vague and not (has_number and has_exact_unit):
        status = "vague"
    elif is_range:
        status = "range"
    elif has_number and has_exact_unit:
        status = "exact"
    elif has_number:
        status = "count"
    elif not has_number:
        status = "missing" if not is_vague else "vague"
    else:
        status = "exact"

    # Identify unit
    unit_found = None
    for u in ['cup', 'katori', 'tbsp', 'tablespoon', 'tsp', 'teaspoon', 'karchi', 'ladle', 'spoon', 'gm', 'g', 'ml', 'pinch']:
        if re.search(r'\b' + re.escape(u) + r'\b', line_clean):
            unit_found = u
            break
    if "thoda" in line_clean or "little" in line_clean:
        unit_found = "thoda"

    return status, is_liver, liver_cat, unit_found

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
        if any(h in lower for h in ["ingredient", "ingredients", "सामग्री", "samagri", "written recipe"]):
            in_ingr_section = True
            continue
        if in_ingr_section:
            if any(stop in lower for stop in ["step by step", "method", "instructions", "subscribe", "social media", "follow me", "music", "gear", "disclaimer", "official website", "check out", "my gears", "amazon", "connect with"]):
                in_ingr_section = False
                continue
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

def run_t7():
    print("Starting T7 YouTube quantity coverage test across 20 fixed dishes x top 3 videos = 60 videos...")
    video_records = []
    ingredient_records = []

    for dish_id, search_term in DISHES:
        print(f"\n=== Searching YouTube for: {dish_id} ('{search_term}') ===")
        vids = get_top_videos(search_term, max_vids=3)
        print(f"  Found {len(vids)} video candidates.")

        for v in vids:
            vid_id = v.get("id")
            title = v.get("title", "")
            channel = v.get("channel", "") or v.get("uploader", "")
            views = v.get("view_count", 0)
            duration = v.get("duration", 0)
            url = f"https://www.youtube.com/watch?v={vid_id}"

            print(f"  -> Processing: [{channel}] {title[:50]}...")
            details = get_video_details(vid_id)
            desc = details.get("description", "") if details else v.get("description", "")

            # 1. Description check
            desc_ingrs = extract_ingredients_from_desc(desc)
            has_desc_ingrs = len(desc_ingrs) >= 3

            # 2. Transcript check
            has_trans, trans_text = analyze_transcript(vid_id)

            source_used = "description" if has_desc_ingrs else ("transcript" if has_trans else "none")

            # Check frying oil quantification
            is_deep_fried = dish_id in DEEP_FRIED_DISHES
            frying_oil_quantified = False

            if has_desc_ingrs:
                for line in desc_ingrs:
                    st, is_liver, cat, unit = classify_yt_line(line)
                    if is_deep_fried and "oil" in line.lower() and any(k in line.lower() for k in ["fry", "deep fry"]):
                        if st in ["exact", "range"]:
                            frying_oil_quantified = True
                    
                    ingredient_records.append({
                        "dish_id": dish_id,
                        "video_id": vid_id,
                        "channel": channel,
                        "source": "description",
                        "raw_line": line,
                        "status": st,
                        "is_liver_relevant": is_liver,
                        "liver_category": cat,
                        "unit": unit
                    })
            elif has_trans:
                # Search transcript for liver mentions
                for cat, kws in LIVER_KEYWORDS.items():
                    for kw in kws:
                        matches = re.finditer(r'([^.!?\n]{0,40}\b' + re.escape(kw) + r'\b[^.!?\n]{0,40})', trans_text, re.IGNORECASE)
                        for m in list(matches)[:2]: # max 2 snippets per keyword
                            snip = m.group(1).strip()
                            st, is_liver, cat_f, unit = classify_yt_line(snip)
                            if is_deep_fried and kw in ["oil", "tel"] and any(k in snip.lower() for k in ["fry", "deep fry", "talne"]):
                                if st in ["exact", "range"]:
                                    frying_oil_quantified = True
                            ingredient_records.append({
                                "dish_id": dish_id,
                                "video_id": vid_id,
                                "channel": channel,
                                "source": "transcript",
                                "raw_line": snip,
                                "status": st,
                                "is_liver_relevant": True,
                                "liver_category": cat,
                                "unit": unit
                            })

            video_records.append({
                "dish_id": dish_id,
                "video_id": vid_id,
                "title": title,
                "channel": channel,
                "views": views,
                "duration_seconds": duration,
                "url": url,
                "has_desc_ingredients": has_desc_ingrs,
                "desc_ingredient_count": len(desc_ingrs),
                "has_transcript": has_trans,
                "source_used": source_used,
                "is_deep_fried_dish": is_deep_fried,
                "frying_oil_quantified": frying_oil_quantified
            })

            time.sleep(1.0) # Polite pause

    df_vids = pd.DataFrame(video_records)
    df_ingrs = pd.DataFrame(ingredient_records)

    df_vids.to_csv("data/t7_youtube_videos.csv", index=False)
    df_ingrs.to_csv("data/t7_youtube_ingredients.csv", index=False)

    print("\nSaved data/t7_youtube_videos.csv and data/t7_youtube_ingredients.csv!")
    print(f"Total videos processed: {len(df_vids)}")
    print(f"% Videos with ingredients in description: {df_vids['has_desc_ingredients'].mean()*100:.1f}%")
    print(f"% Videos with transcripts: {df_vids['has_transcript'].mean()*100:.1f}%")

if __name__ == "__main__":
    run_t7()
