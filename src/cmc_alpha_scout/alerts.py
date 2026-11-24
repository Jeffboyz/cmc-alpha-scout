"""Simple threshold alerts, written to console/log.

Alerting is deliberately transport-agnostic: emit() prints to stdout and
appends to an optional log file. A Telegram/Discord sender can subscribe
to the same Alert objects later without touching the detection logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Alert:
    symbol: str
    kind: str        # e.g. "price_move_24h", "volume_spike"
    message: str
    when: str = ""

    def __str__(self) -> str:
        return f"[ALERT {self.when}] {self.symbol} {self.kind}: {self.message}"


def detect_alerts(listings: list[dict], *, move_threshold_pct: float = 5.0,
                  min_volume_24h: float = 100_000_000) -> list[Alert]:
    """Flag coins with |24h change| >= threshold on meaningful volume."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    alerts: list[Alert] = []
    for coin in listings:
        q = coin.get("quote", {}).get("USD", {})
        change = q.get("percent_change_24h")
        volume = q.get("volume_24h") or 0
        if change is None:
            continue
        if abs(change) >= move_threshold_pct and volume >= min_volume_24h:
            alerts.append(Alert(
                symbol=coin.get("symbol", "?"),
                kind="price_move_24h",
                message=(f"{change:+.2f}% in 24h at ${q.get('price'):,.2f} "
                         f"(vol24h ${volume:,.0f})"),
                when=now,
            ))
    return alerts


def emit(alerts: list[Alert], log_path: str | None = None) -> None:
    if not alerts:
        print("Alerts: none triggered.")
        return
    print(f"Alerts: {len(alerts)} triggered")
    lines = []
    for alert in alerts:
        print(str(alert))
        lines.append(str(alert))
    if log_path:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
