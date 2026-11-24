"""Daily market summary from CMC global metrics + Fear & Greed index."""
from __future__ import annotations


def build_summary(global_metrics: dict, fear_greed: dict | None,
                  trending: list[dict]) -> str:
    usd = global_metrics.get("quote", {}).get("USD", {})
    lines = ["=== DAILY MARKET SUMMARY ==="]
    mcap = usd.get("total_market_cap")
    if mcap is not None:
        chg = usd.get("total_market_cap_yesterday_percentage_change")
        chg_txt = f" ({chg:+.2f}% vs yesterday)" if chg is not None else ""
        lines.append(f"Total market cap : ${mcap:,.0f}{chg_txt}")
    vol = usd.get("total_volume_24h")
    if vol is not None:
        lines.append(f"Total volume 24h : ${vol:,.0f}")
    if global_metrics.get("btc_dominance") is not None:
        lines.append(f"BTC dominance    : {global_metrics['btc_dominance']:.1f}%")
    if global_metrics.get("eth_dominance") is not None:
        lines.append(f"ETH dominance    : {global_metrics['eth_dominance']:.1f}%")
    if global_metrics.get("active_cryptocurrencies") is not None:
        lines.append(f"Active cryptos   : {global_metrics['active_cryptocurrencies']:,}")
    if fear_greed:
        lines.append(
            f"Fear & Greed     : {fear_greed.get('value')} "
            f"({fear_greed.get('value_classification')})"
        )
    else:
        lines.append("Fear & Greed     : n/a (index unavailable on this plan)")
    if trending:
        names = ", ".join(f"{c['symbol']} (#{c.get('cmc_rank')})" for c in trending[:5])
        lines.append(f"Trending         : {names}")
    return "\n".join(lines)
