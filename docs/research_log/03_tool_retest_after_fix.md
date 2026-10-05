# 03 Stealth Search re-test after user's fixes (2026-09-29)

| Test | Result | Status |
|---|---|---|
| fast_neural_search, 4 pages, PPGR query (was 457,542 chars) | 457,543 chars again, errored out of the tool-result limit | STILL BROKEN |
| fetch iiitd.ac.in/gastrosym2025 (was SEC_ERROR_UNKNOWN_ISSUER) | identical SSL error | STILL BROKEN |
| fetch researchgate.net/publication/... (was "extracted content was empty") | identical message | STILL BROKEN (message unchanged) |
| fetch nature.com article, default mode (was "JavaScript is disabled") | identical JS-disabled text returned as content | STILL BROKEN in default mode |
| fetch nature.com article, force_browser=true | full article returned, clean markdown | WORKS |

## Root cause of the 457K blowup (diagnosed from the saved output)
- 4 sources returned; sources 1-3 (HTML) total ~8.6K chars.
- Source 4 was a medRxiv `.full.pdf`. The tool put RAW PDF BYTES into "Key Passages": `%PDF-1.4`, `endobj`, `<>stream`, compressed binary. ~438K chars = 98% of the output.
- So: PDFs are not parsed to text in fast_neural_search, and there is no output size cap.

## Other observed defects this round
- Failed/blocked fetches (JS-disabled page) still returned as if they were page content.
- Entity extractor output `2026-09-29T05` tagged as `deadline` (came from the PDF binary).
- "Are you a robot?" page (ScienceDirect) returned as a Key Passage with relevance -9.99.
- Nature page with force_browser: "Similar content being viewed by others" boilerplate included, and Received/Accepted/Published fields blank.
- Default fetch does not auto-fall-back to browser mode when it detects a JS-disabled page (a simple heuristic would fix this).

# Round 2 re-test (after user's second update)
| Test | Result | Status |
|---|---|---|
| fast_neural_search PPGR query, 4 pages | 457,542 chars again; source #3 = medRxiv .full.pdf = 438,752 chars of raw PDF bytes (1x `%PDF-`, 73x `endobj`); HTML sources total ~8.6K | STILL BROKEN |
| fetch medrxiv .full.pdf directly | 447,981 chars, exceeds limit (same raw-bytes problem in fetch, not only in fast_neural_search) | STILL BROKEN |
| fetch nature.com article, default mode (force_browser=false) | full clean article returned | FIXED (auto JS fallback works) |
| fetch iiitd.ac.in/gastrosym2025 | same SEC_ERROR_UNKNOWN_ISSUER | STILL BROKEN |
| fetch researchgate | not re-tested this round | UNKNOWN |

Remaining bugs: (1) PDF -> text parsing missing in BOTH fetch and fast_neural_search; (2) no global output cap;
(3) TLS-chain error on iiitd.ac.in with no fallback. Workaround: avoid direct .pdf URLs; prefer HTML/abstract landing pages; use `search` for compact snippets.

# Round 3 re-test (after /mcp reconnect) : ALL PRIOR FAILURES FIXED
| Test | Result | Status |
|---|---|---|
| fetch medrxiv .full.pdf | parsed to text per page ("## Page N"), capped at 25,000 chars with a note pointing to get_toc/read_section | FIXED |
| fast_neural_search PPGR query (was 457K) | 9,731 chars (~2.3K tokens), PDF parsed, passages with % match, "Top Finding" up top | FIXED |
| bot-check page (ScienceDirect) | listed under "Inaccessible / Blocked Sources" footer, not as content | FIXED |
| fetch iiitd.ac.in/gastrosym2025 | full page content returned (SSL error gone) | FIXED |
| New tool exposed after reconnect: mcp__stealth-search__batch_search (not yet loaded/tested) | - | UNTESTED |
Cause of earlier "still broken": MCP server process needed /mcp reconnect to load the new code.
Minor remaining: passages end with "[... Passage truncated ...]" mid-sentence (acceptable).
