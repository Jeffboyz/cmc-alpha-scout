"""CMC Alpha Scout CLI.

Usage:
  python -m cmc_alpha_scout summary                 # daily market summary
  python -m cmc_alpha_scout screen [--top 10] [--min-change 2] [--min-volume 1000000]
  python -m cmc_alpha_scout alerts [--threshold 5] [--log alerts.log]
  python -m cmc_alpha_scout all                     # summary + screen + alerts

Add --demo to force sample data, or just leave CMC_API_KEY unset.
"""
from __future__ import annotations

import argparse
import sys

from . import alerts as alerts_mod
from . import screener, summary
from .client import CMCClient, CMCError

DEMO_BANNER = "=" * 64 + "\n  DEMO MODE — SAMPLE DATA (not live market data)\n" + "=" * 64


def _client(args) -> CMCClient:
    client = CMCClient(demo=args.demo)
    if client.demo:
        print(DEMO_BANNER)
    else:
        print("LIVE MODE — CoinMarketCap API")
    return client


def cmd_summary(args) -> int:
    client = _client(args)
    text = summary.build_summary(client.global_metrics(),
                                 client.fear_and_greed(),
                                 client.trending())
    print(text)
    return 0


def cmd_screen(args) -> int:
    client = _client(args)
    result = screener.screen(client.listings_latest(limit=args.limit),
                             min_change_24h=args.min_change,
                             min_volume_24h=args.min_volume,
                             top=args.top)
    print("=== TOP GAINERS 24h ===")
    print(screener.format_table(result["gainers"]))
    print("=== TOP LOSERS 24h ===")
    print(screener.format_table(result["losers"]))
    return 0


def cmd_alerts(args) -> int:
    client = _client(args)
    found = alerts_mod.detect_alerts(client.listings_latest(limit=args.limit),
                                     move_threshold_pct=args.threshold,
                                     min_volume_24h=args.min_volume)
    alerts_mod.emit(found, log_path=args.log)
    return 0


def cmd_all(args) -> int:
    rc = cmd_summary(args)
    print()
    rc |= cmd_screen(args)
    print()
    rc |= cmd_alerts(args)
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cmc-alpha-scout",
                                     description="CoinMarketCap-powered crypto research agent")
    parser.add_argument("--demo", action="store_true",
                        help="force demo mode with sample data")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("summary", help="daily market summary").set_defaults(func=cmd_summary)

    p_screen = sub.add_parser("screen", help="momentum/volume screener")
    p_screen.add_argument("--top", type=int, default=5)
    p_screen.add_argument("--limit", type=int, default=100)
    p_screen.add_argument("--min-change", type=float, default=0.0,
                          help="minimum |24h %% change| to include")
    p_screen.add_argument("--min-volume", type=float, default=0.0,
                          help="minimum 24h volume in USD")
    p_screen.set_defaults(func=cmd_screen)

    p_alerts = sub.add_parser("alerts", help="threshold alerts to console/log")
    p_alerts.add_argument("--threshold", type=float, default=5.0,
                          help="|24h %% change| that triggers an alert")
    p_alerts.add_argument("--limit", type=int, default=100)
    p_alerts.add_argument("--min-volume", type=float, default=100_000_000)
    p_alerts.add_argument("--log", default=None, help="append alerts to this log file")
    p_alerts.set_defaults(func=cmd_alerts)

    p_all = sub.add_parser("all", help="summary + screen + alerts")
    p_all.add_argument("--top", type=int, default=5)
    p_all.add_argument("--limit", type=int, default=100)
    p_all.add_argument("--min-change", type=float, default=0.0)
    p_all.add_argument("--min-volume", type=float, default=0.0)
    p_all.add_argument("--threshold", type=float, default=5.0)
    p_all.add_argument("--log", default=None)
    p_all.set_defaults(func=cmd_all)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CMCError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
