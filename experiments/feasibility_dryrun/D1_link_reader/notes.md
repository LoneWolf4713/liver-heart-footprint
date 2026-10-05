# D1 Link Reader Notes

- Attempted 62 recipes across 10 dishes and 7 domains.
- Successfully fetched 43 recipes with 100% schema.org Recipe JSON-LD on accessible domains.
- Blocked: 8 attempts (8/62) on vegrecipesofindia.com and tarladalal.com due to Cloudflare anti-bot challenges (logged in exclusions.csv under I7).
- Recipe identity check (I6): 43 passed, 0 mismatched among fetched pages.
- Non-salt liver-relevant lines in non-fried dishes: 93.1% (81/87) were exact or range, PASSING the >=80% criterion.
- Deep-fried recipes: 7/12 (58.33%) had unquantified frying oil ('oil for deep frying' / 'as required'), proving the absolute necessity of the D4 frying model.
