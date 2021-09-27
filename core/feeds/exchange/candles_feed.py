import asyncio
import logging
from databases import Database
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta
from core.enums.feed_config import FeedConfig
from core.database.crud.exchange import sync_read_exchange_by_id
from core.database.crud.market import sync_read_markets_by_tags
from core.database.database import get_sync_db
from core.feeds.helpers import has_required_configs
from core.enums.candle_length import CandleLength
from core.models.candle import CandleModel
from core.elasticsearch.api import ElasticApiHelper


def load_candle(candle_data: dict):
    try:
        return CandleModel(**candle_data)
    except ValidationError as ve:
        logging.error(
            f"Load Candle : ValidationError : CandleModel : Market {market.symbol} : Data {ve.json()}"
        )
    except TypeError as te:
        logging.error(
            f"Load Candle : TypeError : Input Must be a Dict : Data {str(te)}"
        )
    return None


def fetch_candle(es_client, index_name, template_name, market_symbol, exchange_id):
    params = {
        FeedConfig.MarketSymbol.value: market_symbol,
        FeedConfig.ExchangeID.value: exchange_id,
    }
    results = es_client.template_search(template_name, index_name, params)
    if not results:
        return None
    else:
        return load_candle(**results[0].get("_source"))


def candle_result_generator(configs: dict, index_name: str, **kwargs):
    exchange_ids = None
    market_tags = None
    required_configs = [
        FeedConfig.MarketTags,
        FeedConfig.CandleLength,
        FeedConfig.NewestCandle,
        FeedConfig.StartAt,
        FeedConfig.MaxResults,
        FeedConfig.MaxResultsPerMarket,
    ]
    if not has_required_configs(required_configs, configs):
        logging.error("Candle Result Generator : Missing Feed Configs")
        return
    market_tags = configs.get(FeedConfig.MarketTags.value)
    try:
        length = CandleLength(configs.get(FeedConfig.CandleLength.value))
    except ValueError as ve:
        logging.error(
            "Candle Result Generator : ValueError : Length Config Must be a CandleLength"
        )
        return
    newest_candle_template_name = configs.get(FeedConfig.NewestCandle.value)

    end_time = datetime.now(tz=timezone.utc) - timedelta(
        days=1
    )  # Can only get results up to 1 day old
    max_results = configs.get(FeedConfig.MaxResults.value)
    max_results_per_market = configs.get(FeedConfig.MaxResultsPerMarket.value)
    result_count = 0
    es_client = ElasticApiHelper()
    engine = get_sync_db()
    with engine.connect() as connection:
        for market in sync_read_markets_by_tags(connection, market_tags):
            exchange = sync_read_exchange_by_id(connection, market.exchange_id)
            if not exchange:
                logging.error(
                    f"Candle Result Generator : Failed to Load Exchange : Exchange ID {exchange_id}"
                )
                continue
            start_time = datetime.fromisoformat(
                configs.get(FeedConfig.StartAt.value)
            ).replace(tzinfo=timezone.utc)
            market_result_count = 0
            newest_candle = fetch_candle(
                es_client,
                index_name,
                newest_candle_template_name,
                market.symbol,
                exchange.id,
            )
            if newest_candle:
                start_time = newest_candle.time
            while start_time < end_time:
                if market_result_count >= max_results_per_market:
                    break
                if result_count > max_results:
                    break
                for candle in exchange.api(exchange).generate_candles(
                    symbol=market.symbol, length=length, start=start_time
                ):
                    market_result_count += 1
                    result_count += 1
                    start_time = candle.time
                    try:
                        yield CandleModel(**candle.dict()).dict()
                    except ValidationError as ve:
                        logging.error(
                            f"Candle Result Generator : ValidationError : CandleModel : {ve.json()}"
                        )
                        continue
            logging.error(
                f"Candle Result Generator : Market Completed : Market {market.symbol} : Market Results {market_result_count} : Total Results {result_count} : Last Record Timestamp {start_time}"
            )
    logging.error(
        f"Candle Result Generator : All Markets Completed : Total Results {result_count}"
    )
    return
