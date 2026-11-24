# CMC Alpha Scout

A CoinMarketCap-powered crypto research agent: it screens the market for
momentum and volume, summarises the day's market in one glance, and fires
simple threshold alerts — the research workflow a solo trader normally
does by hand across five browser tabs, automated into one command.

Built for the **DoraHacks "Build with CMC: API Hackathon" (Round 2)** —
submission deadline **10 Dec 2026, 06:59 WIB**.
Tracks: **AI Agents & Automation** + **Markets & Trading Tools**.

## Features

1. **Screener** — ranks the top-100 CMC listings into top gainers/losers by
   24h price change, filterable by minimum |change| and minimum 24h volume.
2. **Daily market summary** — total market cap (+ change vs yesterday),
   total 24h volume, BTC/ETH dominance, active cryptocurrencies, the CMC
   Fear & Greed Index (when the plan serves it), and trending coins.
3. **Alerts** — flags coins moving ≥ a configurable % in 24h on meaningful
   volume, printed to console and optionally appended to a log file. The
   alert objects are transport-agnostic, ready to be wired to Telegram.

## CoinMarketCap endpoints used

| Endpoint | Used for |
|---|---|
| `GET /v1/cryptocurrency/listings/latest` | Screener input + quotes for the top 100 |
| `GET /v1/cryptocurrency/quotes/latest` | On-demand quotes for specific symbols |
| `GET /v1/global-metrics/quotes/latest` | Market cap, volume, BTC/ETH dominance |
| `GET /v1/cryptocurrency/trending/latest` | Trending coins in the daily summary (plan permitting) |
| `GET /v3/fear-and-greed/latest` | CMC Fear & Greed Index (optional, degrades gracefully) |

API evidence for the submission: run any command in live mode — the client
calls the endpoints above with the `X-CMC_PRO_API_KEY` header; a screen
recording of a live run will be attached to the DoraHacks submission.

## Stack decision

**Python 3 + `requests` only.** Rationale: the whole product is API
orchestration and text reporting, so a single tiny dependency keeps the
demo reproducible anywhere (including a phone-adjacent VM), startup is
instant, and there is no build step. Node would add nothing here.

## Quick start

```bash
pip install -r requirements.txt

# Demo mode — no key needed, uses clearly-labelled SAMPLE data:
PYTHONPATH=src python3 -m cmc_alpha_scout --demo all

# Live mode — get a free key (hackathon participants get the free
# Startup tier during the event, no card):
export CMC_API_KEY=<your key>        # or copy .env.example to .env
PYTHONPATH=src python3 -m cmc_alpha_scout all
```

If `CMC_API_KEY` is unset, the tool automatically falls back to demo mode
and prints a `DEMO MODE — SAMPLE DATA` banner on every run, so it can
never silently present sample figures as live data.

### Commands

```bash
python -m cmc_alpha_scout summary                     # daily summary only
python -m cmc_alpha_scout screen --top 10 --min-change 2 --min-volume 1000000
python -m cmc_alpha_scout alerts --threshold 5 --log alerts.log
python -m cmc_alpha_scout all                         # everything
```

## Tests

```bash
PYTHONPATH=src python3 tests/test_demo.py   # offline, demo-mode assertions
```

## Demo plan (for the submission video / screen recording)

1. Open with the problem: manual daily research across CMC tabs.
2. Run `cmc_alpha_scout all` in **live mode**; walk through the summary
   (Fear & Greed + dominance), the gainers/losers screen, and the alerts.
3. Tighten the screener live (`--min-change 5`) to show filtering.
4. Show an alert landing in `alerts.log`; explain the Telegram hook.
5. Close with the roadmap below.

Submission checklist (from the hackathon rules): public GitHub repo,
working demo / screen recording, X post with **#BuildwithCMC** naming the
CMC endpoints used + proof of real API calls.

## Roadmap

- Telegram bot delivery for alerts (`alerts.py` already emits objects).
- Watchlist file + per-coin quote checks via `quotes/latest`.
- Scheduled daily summary (cron) with a one-paragraph natural-language
  market brief generated from the summary numbers.
- Historical sparklines via CMC historical quotes for the top movers.

## Status

v0.1.0 scaffold — all three core features implemented and verified
offline in demo mode. Live mode is code-complete; it activates as soon as
a `CMC_API_KEY` is provided.
