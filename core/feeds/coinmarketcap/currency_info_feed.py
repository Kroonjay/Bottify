from core.feeds.coinmarketcap.helpers import get_cmc_session
from core.feeds.helpers import action_wrapper
from pydantic import BaseModel, Field, ValidationError
from typing import List
from decimal import Decimal
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import logging
from datetime import datetime, timezone
import os

url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"


class CoinMarketCapCurrencyInfoModel(BaseModel):
    id: str = Field(alias="_id")
    name: str = None
    symbol: str = None
    slug: str = None
    num_market_pairs: int = None
    date_added: datetime = None
    tags: List[str] = None
    max_supply: Decimal = None
    circulating_supply: Decimal = None
    total_supply: Decimal = None
    cmc_rank: int = None
    last_updated_at: datetime = None
    source_id: int = None
    volume_24h: Decimal = None
    percent_change_1h: Decimal = None
    percent_change_24h: Decimal = None
    percent_change_7d: Decimal = None
    percent_change_30d: Decimal = None
    percent_change_60d: Decimal = None
    percent_change_90d: Decimal = None
    market_cap: Decimal = None
    market_cap_dominance: Decimal = None
    fully_diluted_market_cap: Decimal = None
    price_usd: Decimal = None
    parent_source_id: int = None
    token_address: str = None
    source_last_updated_at: datetime = None

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


def parse_currency_info_result(result):
    if not isinstance(result, dict):
        print("Currency Info Result Must be a Dictionary")
        return None

    result.update({"last_updated_at": str(datetime.now(tz=timezone.utc))})
    if "id" in result:
        result.update({"source_id": result["id"]})
        result.pop("id")
    result.update({"id": result["symbol"]})
    if "quote" in result:
        quote = result["quote"]["USD"]
        quote.update({"price_usd": quote["price"]})
        quote.pop("price")
        result.update(quote)
        result.pop("quote")
    if result["platform"]:
        result.update({"parent_source_id": result["platform"]["id"]})
        if "token_address" in result["platform"]:
            result.update({"token_address": result["platform"]["token_address"]})
        result.pop("platform")
    if "last_updated" in result:
        result.update({"source_last_updated_at": result["last_updated"]})
        result.pop("last_updated")
    try:
        return CoinMarketCapCurrencyInfoModel(**result)
    except ValidationError as ve:
        logging.error(
            f"Parse Currency Info Result : CoinMarketCapCurrencyInfoModel : ValidationError : {ve.json()}"
        )
        return None


def cmc_currency_result_generator(configs: dict, **kwargs):
    if not configs:
        logging.error(
            "CoinMarketCap Currency Result Generator : Config is Missing or Invalid"
        )
        return

    cmc_api_key = configs.get("cmc_api_key")
    if not cmc_api_key:
        logging.error(
            f"CoinMarketCap Currency Result Generator : CoinMarketCap API Key Missing"
        )
        return
    if configs.get("start"):
        start_param = configs.get("start")
    else:
        start_param = 1
    if configs.get("limit"):
        limit_param = configs.get("limit")
    else:
        limit_param = 5000
    if configs.get("conversion_currency"):
        convert_param = configs.get("conversion_currency")
    else:
        convert_param = "USD"
    session = get_cmc_session(cmc_api_key)
    parameters = {
        "start": start_param,
        "limit": limit_param,
        "convert": convert_param,
    }
    logging.info(
        f"CoinMarketCap Currency Result Generator : Fetching Data : Params {parameters}"
    )
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        # print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        logging.error(
            f"CoinMarketCap Currency Result Generator : Invalid API Response : Data {str(e)}"
        )
        return
    for item in data["data"]:
        currency_info = parse_currency_info_result(item)
        if currency_info:
            # yield {"_id": currency_info.id, "doc": currency_info.json(exclude={"id"})}
            yield currency_info.dict(by_alias=True)


def main():
    for currency in get_currency_info():
        print(currency)


if __name__ == "__main__":
    main()
