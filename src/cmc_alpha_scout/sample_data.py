"""Demo-mode sample data.

!!! THESE ARE STATIC SAMPLE FIGURES FOR OFFLINE DEVELOPMENT ONLY !!!
They are NOT live market data. Demo mode exists so the project runs and
can be developed/demonstrated before a CoinMarketCap API key is provided.
Every demo-mode output is banner-labelled "DEMO MODE — SAMPLE DATA".
The shapes mirror the real CoinMarketCap API responses so the same code
paths run in both modes.
"""

SAMPLE_LISTINGS = [
    {"id": 1, "name": "Bitcoin", "symbol": "BTC", "cmc_rank": 1,
     "quote": {"USD": {"price": 97412.10, "volume_24h": 48_200_000_000,
                        "percent_change_1h": 0.42, "percent_change_24h": 2.85,
                        "percent_change_7d": 6.10, "market_cap": 1_924_000_000_000}}},
    {"id": 1027, "name": "Ethereum", "symbol": "ETH", "cmc_rank": 2,
     "quote": {"USD": {"price": 3412.55, "volume_24h": 21_400_000_000,
                        "percent_change_1h": -0.18, "percent_change_24h": 3.92,
                        "percent_change_7d": 8.44, "market_cap": 410_500_000_000}}},
    {"id": 1839, "name": "BNB", "symbol": "BNB", "cmc_rank": 3,
     "quote": {"USD": {"price": 692.30, "volume_24h": 1_980_000_000,
                        "percent_change_1h": 0.11, "percent_change_24h": 1.24,
                        "percent_change_7d": 2.02, "market_cap": 101_900_000_000}}},
    {"id": 5426, "name": "Solana", "symbol": "SOL", "cmc_rank": 4,
     "quote": {"USD": {"price": 214.87, "volume_24h": 4_650_000_000,
                        "percent_change_1h": 0.87, "percent_change_24h": 7.63,
                        "percent_change_7d": 12.91, "market_cap": 104_300_000_000}}},
    {"id": 52, "name": "XRP", "symbol": "XRP", "cmc_rank": 5,
     "quote": {"USD": {"price": 2.41, "volume_24h": 5_120_000_000,
                        "percent_change_1h": -0.34, "percent_change_24h": -3.18,
                        "percent_change_7d": 4.55, "market_cap": 138_700_000_000}}},
    {"id": 2010, "name": "Cardano", "symbol": "ADA", "cmc_rank": 8,
     "quote": {"USD": {"price": 0.9821, "volume_24h": 890_000_000,
                        "percent_change_1h": 0.05, "percent_change_24h": -1.47,
                        "percent_change_7d": -2.88, "market_cap": 34_500_000_000}}},
    {"id": 6636, "name": "Polkadot", "symbol": "DOT", "cmc_rank": 12,
     "quote": {"USD": {"price": 8.74, "volume_24h": 310_000_000,
                        "percent_change_1h": 0.29, "percent_change_24h": 5.36,
                        "percent_change_7d": 3.17, "market_cap": 13_300_000_000}}},
    {"id": 5805, "name": "Avalanche", "symbol": "AVAX", "cmc_rank": 13,
     "quote": {"USD": {"price": 41.26, "volume_24h": 520_000_000,
                        "percent_change_1h": 1.12, "percent_change_24h": 9.84,
                        "percent_change_7d": 15.62, "market_cap": 16_900_000_000}}},
]

SAMPLE_GLOBAL = {
    "quote": {"USD": {"total_market_cap": 3_380_000_000_000,
                      "total_volume_24h": 142_000_000_000,
                      "total_market_cap_yesterday_percentage_change": 2.31}},
    "btc_dominance": 56.9,
    "eth_dominance": 12.1,
    "active_cryptocurrencies": 10482,
    "active_exchanges": 812,
}

SAMPLE_FEAR_GREED = {"value": 74, "value_classification": "Greed",
                     "timestamp": "2026-11-25T00:00:00Z"}

SAMPLE_TRENDING = [
    {"id": 5805, "name": "Avalanche", "symbol": "AVAX", "cmc_rank": 13},
    {"id": 5426, "name": "Solana", "symbol": "SOL", "cmc_rank": 4},
    {"id": 6636, "name": "Polkadot", "symbol": "DOT", "cmc_rank": 12},
]
