from enum import IntEnum


class AlertType(IntEnum):
    Unset = 0
    Currency = 1  # For alerts where only Currency is provided
    CurrencyPrice = 2  # For alerts where Currency and Price are provdied (limit order)
    CurrencyExchange = (
        3  # For alerts where Currency and Exchange are provided (market order)
    )
    CurrencyExchangePrice = (
        4  # For alerts where Currency, Exchange, and Price are provided (limit order)
    )

    Market = 5  # For Alerts where only Market is provided
    MarketPrice = 6  # For alerts where Market and Price are provided (limit order)
    MarketExchange = (
        7  # For alerts where Market and Exchange are provided (market order)
    )
    MarketExchangePrice = (
        8  # For alerts where Market, Exchange, and Price are provided (limit order)
    )
