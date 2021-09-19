from core.exchanges.maps import exchange_balance_map, exchange_market_map


def transform_exchange_balance(balance_in, exchange_id, exchange_type, currency_id):
    transformer = exchange_balance_map.get(exchange_type)
    if not transformer:
        logging.error(
            f"Transform Exchange Balance : No Transformer Found for Exchange Type : Exchange Type {str(exchange_type)}"
        )
        return None
    return transformer(balance_in, currency_id=currency_id, exchange_id=exchange_id)


def transform_exchange_market(
    market_in, exchange_id, exchange_type, base_currency_id, quote_currency_id
):
    transformer = exchange_market_map.get(exchange_type)
    if not transformer:
        logging.error(
            f"Transform Exchange Market : No Transformer Found for Exchange Type : Exchange Type {str(exchange_type)}"
        )
        return None
    return transformer(market_in, exchange_id, base_currency_id, quote_currency_id)
