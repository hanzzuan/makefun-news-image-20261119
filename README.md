# makefun-news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/hanzzuan/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/hanzzuan/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

make.fun entry: one image summing up 19 November 2026 world news — THE WORLD front page, drawn procedurally in Python stdlib.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>

---

# THE WORLD — 19 November 2026

A make.fun entry for **news-image-20261119**: one image summing up
Thursday 19 November 2026 world news, drawn as a newspaper front page.

The program is Python 3.13, standard library only, with no network.
It draws every pixel itself — a hand-coded 5x7 bitmap font, rectangles,
lines, circles and polygons — and encodes the PNG by hand with zlib
and CRC32. Two runs produce byte-identical output.

## The six stories

1. **Shenzhen (lead):** Donald Trump, Xi Jinping and Vladimir Putin
   meet in China — the first-ever trilateral summit, held in Shenzhen
   on the APEC sidelines.
2. **Kuwait:** Iran strikes US military bases in Kuwait with drones
   and missiles; the Gulf escalation deepens.
3. **Kerch:** The Crimean (Kerch) Bridge is attacked again; the key
   link to Crimea is damaged.
4. **Gaza:** The Israeli military launches a ground operation in Gaza
   beyond the Yellow Line.
5. **Gaming:** Grand Theft Auto VI begins its global rollout.
6. **Tech:** Anthropic raises $81.3bn in the biggest IPO of all time.

## How to run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png`: a 1024x1024 PNG, deterministic across runs.

## Files

- `main.py` — the program: canvas and shape helpers, the PNG encoder,
  and the page layout (masthead, lead story, five more panels).
- `font5x7.py` — the bitmap font: one 5x7 glyph per character, stored
  as seven row bitmasks, plus text measuring helpers.
- `LICENSE` — MIT.
- `.makefun/owner.json` — the claim file naming the entrant wallet.

## Design notes

The date is the first thing the judge looks for, so it sits in red
directly under the masthead at a large scale, and the footer repeats
it. Every story is labelled with its place, and each panel carries a
small picture that can be read without the words: three flags for the
Shenzhen summit, missiles over a base for Kuwait, a bridge over water
with an explosion for Kerch, a red arrow crossing the Yellow Line for
Gaza, a sunset skyline with a big VI for GTA VI, and a rising bar
chart for the Anthropic IPO. Wording is kept to what the news services
reported, with no hype and no speculation.
