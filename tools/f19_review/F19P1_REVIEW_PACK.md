# F19 phase 1 · independent review pack (for Codex)

Branch `f19-phase1`. Not merged, not deployed. Review the commit that contains this file against:

| Baseline | Commit | Meaning |
|---|---|---|
| frozen technical baseline | `8cc7f94` (tag `f17-f18-accepted-8cc7f94`) | F17/F18 accepted by Codex round 4 (round-4 report text not archived — evidence gap, see `tools/expected/evidence/CODEX_R4_INDEX.md`) |
| pilot | `856a79b` | shared toolbar layout + shared camera safe area, `safeFrame` on l03 l04 l07 l08 |
| this commit | `f19-phase1` HEAD | declarative composition (`compose`) for 12 views of l03 l07 l08 |

## 1. What changed since `856a79b`

- `curs/player.js`
  - `freeRect()` split out of `safeRect()` (same values; proven by the camera comparison below);
  - new `compose(target, dir, opts)`: fits the target into the safe area in screen space; `opts.whole` shows body
    regions entirely, `opts.clear` keeps them out; `clear` may only slide the frame inside the room the target
    leaves, otherwise the region is shown whole (logged as `fallback`). Every call is logged in `ctx.shotLog`.
  - `ctx` exposes `compose` and `shotLog`.
- `curs/l03.js`: `braç`, `braçDarrere`, `tot` → `compose(…, { clear: ['head'] })` (same target, same direction).
- `curs/l07.js`: `braç` → `clear: ['head']`; `tronc`, `esquena` → `whole: ['head']` (same region, same direction).
- `curs/l08.js`: `cap`, `capCostat`, `coll`, `collDarrere`, `davant`, `davantCostat` → `whole: ['head']` via the new
  helper `fc` (same parts, same direction rule as `fs`).
- Tools: `tools/f19_layout.py` (reads `shotLog`; `F19_VIEWS` filter), `tools/f19_phase1/*` (comparison scripts,
  `tap_size.py`, `l10_phone_option.py`).

Unchanged (check with `git diff --stat 8cc7f94 -- <path>`): `app.js`, `index.html`, `lesson.js`, `sample.html`,
`models/`, every lesson file except l03 l04 l07 l08, all questions/answers/scoring/records code, the l10 file.
`curs.html` unchanged since `856a79b`.

## 2. Checks and expected results

Server: `python3 -m http.server 8772 --bind 127.0.0.1` in the checkout (a second checkout of `8cc7f94` / `856a79b` on
another port for comparisons). Software rendering is slow: a view takes about 3 s, a lesson test 5–45 min.

| # | Check | Command | Expected | Evidence |
|---|---|---|---|---|
| 1 | only the 12 composed views changed camera | `tools/f19_layout.py cam` on `856a79b` and HEAD, all 12 lessons, 6 viewports; `tools/f19_phase1/cam_compare.py` | 432 cases; 72 differ = exactly the 12 views × 6 viewports; all other 360 identical | `f19p1b/cam_compare_856a79b_vs_now.txt`, `cam_*_all12.json` |
| 2 | lessons outside the pilot identical to the frozen build | same, `8cc7f94` vs `856a79b` | 246 cases, max difference 0 | `f19p1/cam_compare.txt` |
| 3 | head never cut by a frame edge (pilot views, 186 cases) | `tools/f19_layout.py views` + `tools/f19_phase1/views_compare.py` | head cut 42 (8cc7f94) → 61 (856a79b) → 0; target outside safe area 0; target under toolbar 0 | `f19p1b/views_compare_*.txt`, `views_now.json` |
| 4 | arm views keep the head out without cutting the arm | `views_now_12_composed_raw.json`, field `req.shot.fallback` | no fallback on any viewport; target `inSafe` = 1 | same |
| 5 | toolbar / panel layout | `tools/f19_layout.py layout` (all 12 lessons, 6 viewports) | 0 overlap; 935/936 panel buttons reachable (the 1: F19-14 below); 720/720 toolbar buttons ≥ 44 px; 30×5 button actions work | `f19p1/layout_check.txt` (layout files unchanged since `856a79b`) |
| 6 | F17/F18 and lessons | `f17_race.py`, `f17_s1_review.py OUT 3`, `b_scenarios.py`, `geo_probe.py`, `curs_test.py` l01 l03 l04 l07 l08 l10 | 0 FAIL each | `f19p1b/regression/` |
| 7 | 17-view comparison, 6 viewports | images | before / pilot / now per view | `f19p1b/sheets17/` |
| 8 | phone (P393) size of tap targets | `tools/f19_phase1/tap_size.py` on both builds, `tap_compare.py` | reported, not a pass/fail gate (open limitation L1) | `f19p1b/tap_size_P393_*`, `phone_full_body.*` |

## 3. Open items (not fixed, not to be reported as done)

| ID | Item | Status |
|---|---|---|
| D | hands/feet partly in the picture in 15 views (53 view×viewport cases): same-arm hand at the wrist in the 3 arm views; the other foot in the 2 foot close-ups; hands at the frame edge in trunk views; single-viewport cases on T820P (tablet portrait, layout F19-08 deferred); l08 `coll` hand is hidden behind the body (the metric ignores occlusion) | per-case review with images (`hand_foot_cases.jpg`); no code change; user decision |
| L1 | phone: model about 23 % smaller (toolbar row + 6 % margins); full-body region 425 → 326 px; parts with smaller side < 44 px 55 → 69 of the name-in-view cases | limitation pending acceptance; tap tests on the phone viewport pass |
| F19-14 | phone l10 `A-pregunta`: third option «Cap de les dues» lies below the visible panel body, its centre under the «Continua» bar; reachable after scrolling 45 px; identical on `8cc7f94` | registered, not fixed, not counted as solved (`f19p1b/l10_phone_option/`) |
| F19-08 | tablet portrait layout (side panel on 820 px) | deferred by the user |
| M | measurement: region visibility ignores occlusion (a hidden hand counts as "in the picture") | known limit of `tools/f19_layout.py` |
| G | GitHub push: `POST git-receive-pack` answers HTTP 403 (read works); see HANDOFF | needs the user |
| R4 | Codex round-4 report text not archived | evidence gap kept open |
