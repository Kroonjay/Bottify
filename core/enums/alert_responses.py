from enum import IntEnum

# TODO Finish this shit...
class AlertResponse(IntEnum):
    NoAction = 0  # Used for Testing, don't do anything
    # Values Between 1-100 are Reserved for Market orders
    # Values Between 1-50 are Reserved for Buy orders
    MarketBuyMax = 1  # Requires: Markets, or Currencies.  Detail: Spent All of available base_currency budget on market buy orders for specified inputs.
    MarketBuyPercentHalf = 2  # Requires: Currencies or Markets.  Detail: Spend Fifty (50%) of available base_currency budget on market buy orders for specified inputs.
    MarketBuyPercentQuarter = 3  # Requires: Currencies or Markets.  Detail: Spend one Quarter (25%) of available base_currency budget on market buy orders for specified inputs.
    MarketBuyPercentTen = 4  # Requires: Currencies or Markets: Detail: Spend Ten Percent (10%) of available base_currency budget on market buy orders for specified inputs.
    MarketBuyUnitOne = 10  # Requires: Currencies or Markets.  Detail: Purchase one unit of input using a market buy order, as long as price is under available base_currency budget.

    MarketSellMax = 51  # Requires: Currencies or Markets.  Detail: Sell all of the available budget for the specified input using a market sell order.
    MarketSellPercentHalf = 52  # Requires: Currencies or Markets.  Detail: Sell Half (50%) of the available budget for the specified input using a market sell order.
    MarketSellPercentQuarter = 53  # Requires: Currencies or Markets.  Detail: Sell One Quarter (25%) of the available budget for the specified input using a market sell order.
    MarketSellPercentTen = 54  # Requires: Currencies or Markets.  Detail: Sell Ten Percent (10%) of the available budget for the specified input using a market sell order.

    MarketSellUnitOne = 60  # Requires: Currencies or Markets.  #Requires: Currencies or Markets.  Detail: Sell One unit of the specified input using a market sell order, as long as we have more than one unit available.

    # Values Between 101-200 are Reserved for Limit Orders
    # Values Between 101-150 are Reserved for Buy Orders
    LimitBuyMax = 101  # Requires: Price and either Currencies or Markets. Detail: Spend all of available base_currency budget on limit buy orders for specified currency or market at specified price.
    LimitBuyPercentHalf = 102  # Requires: Price and either Currencies or Markets.  Detail: Spend Half (50%) of the available budget on limit buy orders for the specified currency or market at specified price.
    LimitBuyPercentQuarter = 103  # Requires: Price and either Currencies or Markets.  Detail: Spend One Quarter (25%) of the available budget on limit buy orders for the specified currency or market at specified price.

    LimitSellMax = 151  # Requires: Price and either Currencies or Markets.  Detail: Sell all of the available budget for the specified currency or market for the specified price using a limit sell order.
