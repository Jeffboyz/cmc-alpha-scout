"""Offline smoke tests — run: PYTHONPATH=src python3 tests/test_demo.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmc_alpha_scout import alerts, screener, summary
from cmc_alpha_scout.client import CMCClient


def main() -> int:
    client = CMCClient(api_key="", demo=True)
    assert client.demo, "client without key must be in demo mode"

    listings = client.listings_latest(limit=100)
    assert len(listings) == 8, f"expected 8 sample listings, got {len(listings)}"

    result = screener.screen(listings, top=3)
    assert result["gainers"][0]["symbol"] == "AVAX", result["gainers"]
    assert result["losers"][0]["symbol"] == "XRP", result["losers"]

    filtered = screener.screen(listings, min_volume_24h=1_000_000_000, top=10)
    assert all(r["volume_24h"] >= 1_000_000_000
               for r in filtered["gainers"] + filtered["losers"])

    text = summary.build_summary(client.global_metrics(),
                                 client.fear_and_greed(),
                                 client.trending())
    assert "DAILY MARKET SUMMARY" in text and "Greed" in text, text

    found = alerts.detect_alerts(listings, move_threshold_pct=5.0,
                                 min_volume_24h=100_000_000)
    symbols = {a.symbol for a in found}
    assert symbols == {"SOL", "AVAX", "DOT"}, symbols

    quotes = client.quotes_latest(["BTC", "ETH"])
    assert set(quotes) == {"BTC", "ETH"}, quotes

    print("ALL DEMO TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
