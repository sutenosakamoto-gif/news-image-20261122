# World News — 22 November 2026 (one-image summary)

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/sutenosakamoto-gif/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/sutenosakamoto-gif/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A one-image infographic summarising six major world news stories of
Sunday, 22 November 2026, prepared as a local draft entry for the
make.fun bounty "Sum up 22 November's world news in one image"
(final deadline 2026-11-24 09:00 JST). Nothing has been submitted.

## Contents

- `main.py` — the entry point: standard-library only, self-contained,
  writes the embedded PNG to `/output/entry.png` (no network).
- `entry.png` — the rendered image: 1024×1024, 137,461 bytes,
  sha256 `3255244be7a2f19a9f7ef8c93b4b34f38fd79b01c6235d55ad68f7b51446e504`
- `SOURCES.md` — the six stories, their sources (outlet + date) and URLs.
- `output/entry.png` — output produced by running `main.py` (byte-identical
  to `entry.png`).

## How to run

```bash
python3 main.py   # standard library only, no dependencies
```

`main.py` writes `entry.png` to `/output/entry.png`, falling back to
`./output/entry.png` next to the script when `/output` is not writable.
The render is deterministic: repeated runs produce identical bytes
(verified by sha256 across two runs and across both output locations).

## The six stories

1. COP31 climate talks collapse without a deal (Al Jazeera / Reuters)
2. Drone strike on homes in Dymer leaves 14 missing (Reuters)
3. Three Russian missiles flew into Poland (Reuters)
4. Mexico captures cartel boss 'El Chapo Isidro' (AP / Al Jazeera)
5. Fighting near Congo Ebola outbreak disrupts response (Reuters)
6. Suspected drone attack hits Russian ship at Benghazi (Reuters)

## Submission layout

- `main.py` — the entry point. Standard-library only and self-contained:
  it writes the embedded PNG to `/output/entry.png`, byte-identical on
  every run, with no network access.
- `render_entry.py` — the Pillow script that originally drew `entry.png`.
  It is kept for provenance and is not needed to run the entry.
- `.makefun/owner.json` — claim file naming the linked Solana wallet
  that receives any reward.
