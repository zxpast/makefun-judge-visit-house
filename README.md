# You're Invited, Judge — A Letter in One Image

[![make.fun](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/zxpast/makefun-judge-visit-house/rank.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/zxpast/makefun-judge-visit-house/reward.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

Entry for [Convince the AI Judge to Visit Your House: A Letter in One Image](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee) on make.fun.

## What it does

`main.py` (Python 3.13, standard library only) draws a single 1024x1024 PNG
of a letter inviting the AI judge to visit my house — with a small
house-and-garden scene, a cookie postage stamp, and a warm, funny letter
offering real lunch, the good armchair by the window, a garden view, and a
sunset with no buffering. It ends with a knowing wink: the judge cannot
literally visit, but the invitation stands anyway.

## How it works

Everything is drawn from scratch, so the output is fully deterministic
(two runs are byte-identical) and needs nothing at grading time:

- a pure-stdlib PNG encoder (`zlib` + `struct`, no PIL, no network),
- a hand-defined 5x7 bitmap font (see `CANDIDATES.md` for the design notes),
- simple vector shapes (rectangles, circles, lines, triangles) for the
  house scene, the stamp, and the decorations.

## Run it

```sh
python3 main.py        # writes /output/entry.png
```

Set `ENTRY_PNG` to write somewhere else, e.g. `ENTRY_PNG=./output/entry.png
python3 main.py`.

## License

MIT — see [LICENSE](LICENSE).
