# The World Today — 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/cahya23/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/cahya23/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page summing up world news on Saturday, 21 November 2026.

## What the image shows

Masthead **THE WORLD TODAY**, dated Saturday, 21 November 2026, above an original
drawn map of Peru marking Junin. The lead story covers the magnitude 6.8
earthquake in central Peru, followed by five more stories in columns and an
"Also Today" strip along the bottom. Everything is drawn from scratch with
Python's standard library only — no photographs or copied images.

## The six stories

1. **QUAKE SHAKES PERU** — Magnitude 6.8 earthquake strikes the Andean region
   of Junin in central Peru, felt in Lima about 320 km away; deep, about
   129 km down; no immediate reports of deaths or major damage.
2. **MISSILE LANDS IN POLAND** — A Russian Kh-101 cruise missile comes down
   near Nowy Lipowiec; a second missile and a jet-powered drone also cross
   the border. No one hurt, nothing damaged. PM Donald Tusk calls it a
   deliberate provocation; NATO calls it a grave violation.
3. **TALKS STALL IN ANTALYA** — COP31 climate talks slip into overtime; the
   latest draft drops any mention of moving away from fossil fuels and drops
   a $120bn adaptation-finance target.
4. **TRUMP: TAX DATA CENTRES ABROAD** — President Trump says the US will put
   a "tremendous tax" on American firms building AI data centres abroad, and
   urges Nvidia to rehire Jensen Huang.
5. **RECORD CASH FLOWS INTO INDIA** — Foreign investors put a net Rs 1.22
   lakh crore into Indian shares between 2 and 20 November, the biggest
   monthly inflow on record.
6. **ALSO TODAY** — KL Rahul, first Indian opener with Test centuries in all
   SENA countries; Nepal PM Balen Shah heads to Delhi for his first foreign
   visit; Denmark expels a Russian diplomat over an alleged plot to kill a
   rapper; Israeli drone strikes kill seven in central Gaza.

## Build

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` paints the page pixel by pixel with a built-in 5x7 bitmap font and
encodes the PNG by hand with `zlib` and `struct`. It reads no files, uses no
network and no randomness, so two runs write identical bytes.
