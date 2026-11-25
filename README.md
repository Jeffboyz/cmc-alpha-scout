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

## Live API evidence (verified 25 Nov 2026)

A full live run was executed against the real CoinMarketCap Pro API on
25 Nov 2026 (~00:33 UTC) and the complete transcript is committed at
[`files/live-api-evidence-2026-11-25.txt`](files/live-api-evidence-2026-11-25.txt).
Highlights from that run (all responses `error_code: 0` unless noted):

- `GET /v1/key/info` — key valid, plan credit limit 15,000/month.
- `GET /v1/global-metrics/quotes/latest` — total market cap
  $2,043,449,479,556, BTC dominance 58.6%, data timestamped seconds earlier.
- `GET /v1/cryptocurrency/listings/latest` — screener ranked the top 100;
  top gainer ELF +33.66% (24h), top loser MON −19.00% (24h).
- `GET /v1/cryptocurrency/quotes/latest?symbol=BTC,ETH` — live quotes OK.
- `GET /v3/fear-and-greed/latest` — value **8, "Extreme fear"**.
- Alerts fired on real moves (e.g. 0G −13.6% in 24h on $128M volume).
- `GET /v1/cryptocurrency/trending/latest` — returned HTTP 403
  (error 1006, "plan doesn't support this endpoint") on this plan; the app
  degrades gracefully and the summary simply omits trending coins.

## Notes on the CoinMarketCap API (strengths & limits)

**Strengths**

- One `listings/latest` call returns rank, price, 24h/7d change and volume
  for 100 assets — enough to power a screener, quotes view and alert engine
  from a single credit-efficient request.
- `global-metrics` gives market cap, volume and dominance in one call, and
  the v3 Fear & Greed endpoint adds a sentiment signal most APIs don't have.
- Consistent `status` envelope (`error_code`, `credit_count`, timestamps)
  makes error handling and credit budgeting straightforward.

**Limits found while building**

- Endpoint access is plan-gated in ways that only surface at call time:
  `trending/latest` returns HTTP 403 / error 1006 on this plan, so
  optional features must be coded to degrade gracefully.
- `error_code` is an integer on most endpoints but a **string** (`"0"`) on
  the v3 Fear & Greed endpoint — clients must normalise before testing it
  (Alpha Scout does; see `_status_is_error` in `client.py`).
- Data freshness is excellent (seconds), but every call costs credits, so
  batch endpoints (`listings`, `quotes` with multiple symbols) are strongly
  preferable to per-coin polling.

## Alternative auth: Muse connector proxy transport

In Muse-connected environments the app can run without a local key:
set `CMC_TRANSPORT=proxy` and requests are sent via `urllib` with the
credential injected by the Muse custom-connector proxy
(`dynamic_credentials.add_surrogate_to_request`, connector
`custom.coinmarketcap`, host `pro-api.coinmarketcap.com`). The key is never
visible to the app or the user in that mode. This is optional and additive —
the default transport remains the plain `X-CMC_PRO_API_KEY` header described
above, unchanged for judges and other users.

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

# Live mode via Muse connector proxy (no local key; optional):
CMC_TRANSPORT=proxy PYTHONPATH=src python3 -m cmc_alpha_scout all
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

v0.2.0 — all three core features implemented and verified offline in demo
mode, and **verified live against the real CoinMarketCap Pro API on
25 Nov 2026** (full transcript in `files/live-api-evidence-2026-11-25.txt`).
An optional proxy transport (`CMC_TRANSPORT=proxy`) supports Muse
connector environments; the default API-key transport is unchanged.
