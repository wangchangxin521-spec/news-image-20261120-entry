# One Day in the News — 20 November 2026

Entry for the make.fun competition `news-image-20261120` ("Sum up
20 November's world news in one image", $250).

## The image

A 1024×1024 newspaper front page for **Friday 20 November 2026**,
built from the stories the world's news services were reporting on
that morning (09:15 CST / 01:15 UTC):

1. **U.S. · Iran — Trump defers Iran decision to 2027.**
   President Trump said the U.S. will "see what happens" with Iran
   after 1 January, in a Fox News interview during his trip to China.
   (Reuters)
2. **Russia · Ukraine — Putin: no truce after bridge hit again.**
   Ukraine struck the Crimea Bridge for a third time in a week;
   Putin vowed a harsh response and dropped any idea of a moratorium
   on strikes against energy and shipping. (The Japan Times)
3. **The Hague — Myanmar guilty of genocide.** The U.N.'s top court
   ruled Myanmar committed genocide against the Rohingya Muslim
   minority. (BBC / The Japan Times)
4. **Markets — Anthropic shares soar on debut.** The record
   $81.3bn IPO closed up 17% in its first Nasdaq trade. (CNA / NST)
5. **India — 300,000 flee as cyclone nears.** Cyclone Akvan was due
   on the Odisha coast, with 300,000 people evacuated and 39 trains
   cancelled. (The Hindu / NDTV)

## How it was built

- `build_image.py` composes `entry.png` from the four panel photos in
  `panels/` (AI-generated news-style illustrations, no text in them)
  plus a candlestick chart drawn in code for the IPO story, and lays
  out the masthead, headlines and source line with PIL
  (DejaVu Sans). Re-running it reproduces the same image.
- `main.py` is the competition entry point (Python standard library
  only): it copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
  It runs with no network and writes identical bytes on every run.

## Files

- `entry.png` — the entry, 1024×1024 PNG, under the 1 MiB cap
- `build_image.py` — builds `entry.png` from `panels/`
- `main.py` — entry point (copies `entry.png` to the output dir)
- `panels/` — the four generated panel photos
- `LICENSE` — MIT

## License

MIT — see `LICENSE`.
