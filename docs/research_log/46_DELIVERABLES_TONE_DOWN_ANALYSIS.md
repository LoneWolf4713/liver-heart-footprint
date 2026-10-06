# 46 Deliverables: tone-down analysis after meeting the professor (2026-10-06)
Professor's guidance (reported by the user): deliverables must be crisp and verifiable; vague promises lose marks. User's decision: 4 deliverables, drop D4 (Atlas).
Status of the build: Phase 1 package locked, T1-T9 not started (git 3dd2bb2).

## Problems in the submitted wording (unverifiable phrases)
- D1: "validated model", "category x setting range model", "trans-fat shift under oil reuse" (data for setting x oil strata is thin: 61 verified rows).
- D2: "Liver and Heart profiles with evidence-based weightings" (a weighted index cannot be verified), "regional baselines", "trans fat", "any recipe".
- D3: "authenticity-preserving", "substitution network", "quantile of real recipes" (needs a recipe corpus we do not have; 6 author-stated swaps so far), "pairing fit".
- D4 Atlas: needs thousands of scraped recipes; "by region", "textbook vs web", "street snacks" are open-ended.
- D5: "any recipe link", "day builder", "home-vs-street estimates", "explanations with citations", "evaluated for numeric faithfulness" without a stated test set.

## Proposed crisp versions (numbers chosen so that current data already meets or nearly meets them)
See the chat reply of 2026-10-06 (copied here once the user approves the wording).

## Decision (2026-10-06)
User chose D1 (dataset), D2 (engine), Atlas (now D3), Web app (now D4); substitution engine dropped. Chatbot moved to "possible extensions". Verified today: polite-site sitemaps list hebbarskitchen 4,642, archanaskitchen 10,603, ranveerbrar 1,850, cookwithmanali 690, pipingpotcurry 634 URLs (robots.txt allows recipe pages); INDB has 1,014 recipes, 932 with serving sizes; validation ground truth has 13 lab-analysed dishes. Revised documents: docs/submission/revision_2026-10-06/, master doc section 22.
