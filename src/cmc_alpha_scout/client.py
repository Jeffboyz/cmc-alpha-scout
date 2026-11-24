"""CoinMarketCap API client.

Reads the API key from the CMC_API_KEY environment variable. When no key
is set (or --demo is passed), the client transparently serves the clearly
labelled sample data from sample_data.py so the whole pipeline still runs.

Endpoints used (CoinMarketCap Pro API, https://pro-api.coinmarketcap.com):
  - GET /v1/cryptocurrency/listings/latest   (screener + quotes)
  - GET /v1/cryptocurrency/quotes/latest     (single-asset quotes)
  - GET /v1/global-metrics/quotes/latest     (market-wide summary)
  - GET /v1/cryptocurrency/trending/latest   (trending coins, plan permitting)
  - GET /v3/fear-and-greed/latest            (CMC Fear & Greed Index, optional)
"""
from __future__ import annotations

import os
import sys

import requests

from . import sample_data

BASE_URL = "https://pro-api.coinmarketcap.com"
FEAR_GREED_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"


class CMCError(RuntimeError):
    """Raised when the live CMC API returns an error."""


class CMCClient:
    def __init__(self, api_key: str | None = None, demo: bool = False):
        self.api_key = api_key if api_key is not None else os.environ.get("CMC_API_KEY", "")
        self.demo = demo or not self.api_key
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accepts": "application/json",
            })

    # -- internal ---------------------------------------------------------
    def _get(self, path: str, params: dict | None = None) -> dict:
        try:
            resp = self.session.get(BASE_URL + path, params=params or {}, timeout=30)
        except requests.RequestException as exc:
            raise CMCError(f"network error calling {path}: {exc}") from exc
        try:
            payload = resp.json()
        except ValueError as exc:
            raise CMCError(f"non-JSON response from {path} (HTTP {resp.status_code})") from exc
        status = payload.get("status", {})
        if resp.status_code != 200 or status.get("error_code"):
            raise CMCError(
                f"CMC API error on {path}: HTTP {resp.status_code} "
                f"code={status.get('error_code')} msg={status.get('error_message')}"
            )
        return payload.get("data")

    # -- public API -------------------------------------------------------
    def listings_latest(self, limit: int = 100, convert: str = "USD") -> list[dict]:
        """Latest ranked listings with quotes (screener input)."""
        if self.demo:
            return sample_data.SAMPLE_LISTINGS[:limit]
        return self._get("/v1/cryptocurrency/listings/latest",
                         {"start": 1, "limit": limit, "convert": convert,
                          "sort": "market_cap", "sort_dir": "desc",
                          "cryptocurrency_type": "coins"})

    def quotes_latest(self, symbols: list[str], convert: str = "USD") -> dict:
        """Quotes for specific symbols, e.g. ['BTC', 'ETH']."""
        if self.demo:
            wanted = {s.upper() for s in symbols}
            return {c["symbol"]: c for c in sample_data.SAMPLE_LISTINGS
                    if c["symbol"] in wanted}
        return self._get("/v1/cryptocurrency/quotes/latest",
                         {"symbol": ",".join(symbols), "convert": convert})

    def global_metrics(self, convert: str = "USD") -> dict:
        """Market-wide totals: market cap, volume, BTC/ETH dominance."""
        if self.demo:
            return sample_data.SAMPLE_GLOBAL
        return self._get("/v1/global-metrics/quotes/latest", {"convert": convert})

    def trending(self) -> list[dict]:
        """Trending coins. Optional: returns [] if the plan lacks access."""
        if self.demo:
            return sample_data.SAMPLE_TRENDING
        try:
            data = self._get("/v1/cryptocurrency/trending/latest",
                             {"start": 1, "limit": 10, "time_period": "24h"})
            return data or []
        except CMCError as exc:
            print(f"[cmc] trending unavailable: {exc}", file=sys.stderr)
            return []

    def fear_and_greed(self) -> dict | None:
        """CMC Fear & Greed Index (latest). None when unavailable."""
        if self.demo:
            return sample_data.SAMPLE_FEAR_GREED
        try:
            resp = self.session.get(FEAR_GREED_URL, timeout=30)
            payload = resp.json()
            if resp.status_code != 200:
                return None
            data = payload.get("data")
            if isinstance(data, list):
                return data[0] if data else None
            return data
        except (requests.RequestException, ValueError):
            return None
