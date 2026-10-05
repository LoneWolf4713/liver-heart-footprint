import json
import subprocess
import time
import re

with open("research_log/validation/ground_truth.json", "r") as f:
    dishes = json.load(f)

domains = [
    "indianhealthyrecipes.com",
    "hebbarskitchen.com",
    "archanaskitchen.com",
    "cookwithmanali.com",
    "pipingpotcurry.com"
]

all_urls = {}

for dish in dishes:
    name = dish["dish"]
    valid_links = []
    seen = set()
    print(f"Searching {name} via Stealth Search...")
    for domain in domains:
        if len(valid_links) >= 3:
            break
        cmd = f'/home/prtyksh/tmp/web_search_tool/run_tool.sh search "{name} recipe site:{domain}" --num 5'
        try:
            output = subprocess.check_output(cmd, shell=True, text=True)
            # Find URLs in the output table. They look like https://...
            urls = re.findall(r'https?://[^\s\|]+', output)
            for u in urls:
                if domain in u and u not in seen:
                    if "category" not in u and "tag" not in u and "author" not in u:
                        valid_links.append(u)
                        seen.add(u)
                        if len(valid_links) >= 3:
                            break
        except Exception as e:
            pass
        time.sleep(2)
    all_urls[name] = valid_links[:3]

with open("research_log/validation/urls.json", "w") as f:
    json.dump(all_urls, f, indent=2)

print("Done getting URLs via Stealth Search.")
