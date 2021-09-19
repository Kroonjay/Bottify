import logging

from core.exchanges.bittrex.transformers import (
    transform_balance_bittrex,
    transform_market_bittrex,
)
from core.exchanges.coinbase.transformers import (
    transform_balance_coinbase,
    transform_market_coinbase,
)
from core.exchanges.bittrex.api import BittrexApiHelper
from core.exchanges.coinbase.api import CoinbaseApiHelper
from core.enums.exchanges import Exchange

exchange_balance_map = {
    Exchange.Bittrex: transform_balance_bittrex,
    Exchange.Coinbase: transform_balance_coinbase,
    Exchange.CoinbaseSandbox: transform_balance_coinbase,
}

exchange_market_map = {
    Exchange.Bittrex: transform_market_bittrex,
    Exchange.Coinbase: transform_market_coinbase,
    Exchange.CoinbaseSandbox: transform_market_coinbase,
}


api_map = {
    Exchange.Bittrex: BittrexApiHelper,
    Exchange.Coinbase: CoinbaseApiHelper,
    Exchange.CoinbaseSandbox: CoinbaseApiHelper,
}


def map_api(exchange_type: Exchange):
    if not isinstance(exchange_type, Exchange):
        logging.error(
            f"Map API : Exchange Type Must be a Member of Exchange Enum : Got {type(exchange_type)}"
        )
        return None
    return api_map.get(exchange_type)
