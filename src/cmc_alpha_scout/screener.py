"""Screener: rank coins by 24h price momentum and 24h volume."""
from __future__ import annotations


def _usd(coin: dict) -> dict:
    return coin.get("quote", {}).get("USD", {})


def screen(listings: list[dict], *, min_change_24h: float = 0.0,
           min_volume_24h: float = 0.0, top: int = 10) -> dict:
    """Return {'gainers': [...], 'losers': [...]} filtered + sorted.

    A coin passes the filter when |percent_change_24h| >= min_change_24h
    and its 24h volume >= min_volume_24h. Gainers sort by change desc,
    losers by change asc, each capped at `top` rows.
    """
    rows = []
    for coin in listings:
        q = _usd(coin)
        change = q.get("percent_change_24h")
        volume = q.get("volume_24h") or 0
        if change is None or abs(change) < min_change_24h or volume < min_volume_24h:
            continue
        rows.append({
            "rank": coin.get("cmc_rank"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "price": q.get("price"),
            "change_1h": q.get("percent_change_1h"),
            "change_24h": change,
            "change_7d": q.get("percent_change_7d"),
            "volume_24h": volume,
            "market_cap": q.get("market_cap"),
        })
    gainers = sorted((r for r in rows if r["change_24h"] > 0),
                     key=lambda r: r["change_24h"], reverse=True)[:top]
    losers = sorted((r for r in rows if r["change_24h"] < 0),
                    key=lambda r: r["change_24h"])[:top]
    return {"gainers": gainers, "losers": losers}


def fmt_price(price: float | None) -> str:
    if price is None:
        return "n/a"
    if abs(price) >= 1:
        return f"{price:,.2f}"
    return f"{price:.4g}"


def format_table(rows: list[dict]) -> str:
    if not rows:
        return "  (none)"
    lines = []
    for r in rows:
        lines.append(
            f"  #{r['rank']:<4} {r['symbol']:<6} ${fmt_price(r['price']):>12}  "
            f"24h {r['change_24h']:+6.2f}%  7d {r['change_7d']:+6.2f}%  "
            f"vol24h ${r['volume_24h']:,.0f}"
        )
    return "\n".join(lines)
