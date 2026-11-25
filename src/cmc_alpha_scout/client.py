"""CoinMarketCap API client.

Reads the API key from the CMC_API_KEY environment variable. When no key
is set (or --demo is passed), the client transparently serves the clearly
labelled sample data from sample_data.py so the whole pipeline still runs.

Optional proxy transport: when the environment variable CMC_TRANSPORT=proxy
is set, requests go through urllib and the credential is injected by the
Muse custom-connector proxy (dynamic_credentials.add_surrogate_to_request,
connector "custom.coinmarketcap"). No API key is needed in that mode and the
key is never visible to this process. This is an alternative auth path for
Muse-connected environments only; the default transport (plain API key via
the X-CMC_PRO_API_KEY header) is unchanged.

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
import urllib.error
import urllib.parse
import urllib.request

import requests

from . import sample_data

BASE_URL = "https://pro-api.coinmarketcap.com"
FEAR_GREED_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"
CMC_HOST = "pro-api.coinmarketcap.com"
CONNECTOR_ID = "custom.coinmarketcap"
_DYNAMIC_CREDENTIALS_PATH = "/opt/muse/skills/custom-connector-setup/bin"


def _status_is_error(status: dict) -> bool:
    """True when a CMC status block reports an error.

    CMC returns error_code as an int on most endpoints but as a string
    (e.g. "0") on the v3 Fear & Greed endpoint, so normalise before testing.
    """
    code = status.get("error_code")
    return code not in (None, 0, "0", "")


class CMCError(RuntimeError):
    """Raised when the live CMC API returns an error."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):  # noqa: D102 - mirrors connector helper
        raise RuntimeError("redirect refused, verify the endpoint")


class CMCClient:
    def __init__(self, api_key: str | None = None, demo: bool = False):
        self.transport = os.environ.get("CMC_TRANSPORT", "direct").strip().lower()
        self.api_key = api_key if api_key is not None else os.environ.get("CMC_API_KEY", "")
        # In proxy mode the connector injects the credential, so a local key
        # is not required for live mode.
        self.demo = demo or (not self.api_key and self.transport != "proxy")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accepts": "application/json",
            })

    # -- internal ---------------------------------------------------------
    def _get_via_proxy(self, url: str) -> dict:
        """GET a CMC URL through the Muse credential proxy (urllib)."""
        if _DYNAMIC_CREDENTIALS_PATH not in sys.path:
            sys.path.insert(0, _DYNAMIC_CREDENTIALS_PATH)
        try:
            from dynamic_credentials import add_surrogate_to_request, read_json_response
        except ImportError as exc:
            raise CMCError(
                "CMC_TRANSPORT=proxy needs the Muse connector runtime "
                f"({_DYNAMIC_CREDENTIALS_PATH}/dynamic_credentials.py): {exc}"
            ) from exc
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        add_surrogate_to_request(request, CONNECTOR_ID, allowed_hosts=[CMC_HOST])
        try:
            with urllib.request.build_opener(_NoRedirect()).open(request, timeout=30) as resp:
                return read_json_response(resp)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            raise CMCError(f"CMC API error (proxy): HTTP {exc.code} {body[:500]}") from exc
        except (urllib.error.URLError, RuntimeError) as exc:
            raise CMCError(f"network error calling CMC API (proxy): {exc}") from exc

    def _get_payload(self, url: str) -> dict:
        """Full JSON payload for a fully-built URL, via the active transport."""
        if self.transport == "proxy":
            return self._get_via_proxy(url)
        try:
            resp = self.session.get(url, timeout=30)
        except requests.RequestException as exc:
            raise CMCError(f"network error calling {url}: {exc}") from exc
        try:
            return resp.json()
        except ValueError as exc:
            raise CMCError(f"non-JSON response from {url} (HTTP {resp.status_code})") from exc

    def _get(self, path: str, params: dict | None = None) -> dict:
        query = urllib.parse.urlencode(params or {})
        url = BASE_URL + path + (f"?{query}" if query else "")
        payload = self._get_payload(url)
        status = payload.get("status", {})
        if _status_is_error(status):
            raise CMCError(
                f"CMC API error on {path}: "
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
            payload = self._get_payload(FEAR_GREED_URL)
            if _status_is_error(payload.get("status", {})):
                return None
            data = payload.get("data")
            if isinstance(data, list):
                return data[0] if data else None
            return data
        except (CMCError, requests.RequestException, ValueError):
            return None
