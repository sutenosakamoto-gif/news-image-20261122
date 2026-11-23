# World News — 22 November 2026 (one-image summary)

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/sutenosakamoto-gif/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/sutenosakamoto-gif/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A one-image infographic summarising six major world news stories of
Sunday, 22 November 2026, prepared as a local draft entry for the
make.fun bounty "Sum up 22 November's world news in one image"
(final deadline 2026-11-24 09:00 JST). Nothing has been submitted.

## Contents

- `main.py` — the renderer itself and the entry point: standard-library
  only, self-contained, no network. Running it draws the 1024×1024
  infographic and writes it to `/output/entry.png`.
- `SOURCES.md` — the six stories, their sources (outlet + date) and URLs.

## How to run

```bash
python3 main.py   # standard library only, no dependencies
```

Running `python3 main.py` renders the image to `/output/entry.png`,
falling back to `./entry.png` when `/output` is not writable.
The render is deterministic: repeated runs produce byte-identical
output.

## The six stories

1. COP31 climate talks collapse without a deal (Al Jazeera / Reuters)
2. Drone strike on homes in Dymer leaves 14 missing (Reuters)
3. Three Russian missiles flew into Poland (Reuters)
4. Mexico captures cartel boss 'El Chapo Isidro' (AP / Al Jazeera)
5. Fighting near Congo Ebola outbreak disrupts response (Reuters)
6. Suspected drone attack hits Russian ship at Benghazi (Reuters)

## Submission layout

- `main.py` — the entry point and the renderer. Standard-library only
  and self-contained: running `python3 main.py` renders the image to
  `/output/entry.png`, byte-identical on every run, with no network
  access.
- `.makefun/owner.json` — claim file naming the linked Solana wallet
  that receives any reward.
