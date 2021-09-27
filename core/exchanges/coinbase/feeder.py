import cbpro
import time
import logging
import requests
from datetime import datetime, timezone, timedelta
import asyncio
from core.elasticsearch.api import ElasticApiHelper
from core.enums.statuses import BottifyStatus
from core.exchanges.coinbase.models import (
    CoinbaseSocketTickerModel,
    CoinbaseSocketFeederConfig,
)
from core.enums.feed_sources import FeedSources
from core.models.market import MarketModel
from core.database.crud.feeds import read_active_feed_by_type
from core.config import API_BASE_URL
from core.database.database import create_db
from pydantic import ValidationError


class CoinbaseSocketFeeder(cbpro.WebsocketClient):
    def __init__(self, *args, **kwargs):
        configs = kwargs.pop("configs")
        if not isinstance(configs, CoinbaseSocketFeederConfig):
            logging.critical(
                f"Init : Config is Missing or Invalid : Must be CoinbaseSocketFeederConfig Model : Got {type(configs)}"
            )
            return
        self.configs = configs
        self.markets = []
        self.tickers = {}
        self.is_open = False
        if not self.configs.ticker_index_name:
            logging.critical(
                f"Init : CoinbaseSocketFeederConfig : Required Config 'ticker_index_name' not Provided"
            )
            return
        if not API_BASE_URL:
            logging.critical("Init : API_BASE_URL is Required to Fetch Products")
            return
        kwargs.update({"channels": self.configs.channels})
        super(CoinbaseSocketFeeder, self).__init__(*args, **kwargs)

    def set_products(self):
        self.products = []
        endpoint = f"{API_BASE_URL}/markets/exchange/{self.configs.exchange_id}"
        response = requests.get(endpoint, timeout=30)
        for item in response.json():
            try:
                self.markets.append(MarketModel(**item))
            except ValidationError as ve:
                logging.error(
                    f"Set Products : MarketModel : ValidationError : {ve.json()}"
                )
                continue
        if not self.markets:
            logging.error("Set Products : No Markets")
            return None
        for market in self.markets:
            if market.status == BottifyStatus.Active:
                self.products.append(market.symbol)
        if not self.products:
            logging.error(f"Set Products : No Products")
        return self

    def set_ticker(self, ticker):
        if isinstance(ticker, CoinbaseSocketTickerModel):
            self.tickers.update({ticker.product_id: ticker})
        return self

    def set_is_open(self, is_open):
        self.is_open = is_open
        return self

    def gen_ticker_data(self):
        for symbol, ticker in self.tickers.items():
            if isinstance(ticker, CoinbaseSocketTickerModel):
                yield ticker.dict(by_alias=True)
            else:
                logging.error(
                    f"Gen Ticker Data : Invalid Ticker Type : Type {type(ticker)} : Value {ticker}"
                )
                continue

    def on_open(self):
        if not self.configs:
            logging.error(f"Startup Error : Config is Missing or Invalid")
            return
        self.url = self.configs.socket_url

        self.set_products()
        self.set_is_open(True)

    def on_message(self, message):
        message_type = message.pop("type")
        if message_type == "ticker":
            ticker = CoinbaseSocketTickerModel(**message)
            self.set_ticker(ticker)
        else:
            print(f"Message Type: {message_type}")
            print(f"Message: {message}")

    def on_close(self):
        logging.info(f"Coinbase Socket Feeder : Socket Closed")
        self.set_is_open(False)


async def fetch_feed():
    feed_type = FeedSources.CoinbaseTickers
    async with create_db() as database:
        feed = await read_active_feed_by_type(database, feed_type)
        return feed


def run_feeder():
    feed = asyncio.run(fetch_feed())
    if not feed:
        logging.critical(
            "CoinbaseSocketFeeder : Run : No Active Feeds found for Feed Type"
        )
        return None
    try:
        configs = CoinbaseSocketFeederConfig(
            ticker_index_name=feed.index_name, **feed.configs
        )
    except ValidationError as ve:
        logging.critical(
            f"Init : CoinbaseSocketFeederConfig : ValidationError : {ve.json()}"
        )
        return
    csf = CoinbaseSocketFeeder(configs=configs)
    csf.start()
    retries = 0
    elastic = ElasticApiHelper()
    next_update_time = datetime.now(tz=timezone.utc) + timedelta(
        seconds=5
    )  # Bit of a buffer so we can actually get some tickers on the first update

    while True:
        try:
            if not csf.is_open:
                logging.error(
                    "CoinbaseSocketFeeder : Socket Closed Unexpectedly : Attempting to Restart"
                )
                csf.start()
                continue
            current_time = datetime.now(tz=timezone.utc)

            if current_time > next_update_time:

                elastic.index_generator(feed.index_name, csf.gen_ticker_data())
                next_update_time = current_time + timedelta(
                    minutes=feed.update_interval
                )
                logging.error(
                    f"CoinbaseSocketFeeder : Elastic Upload Overdue : Completed Successfully : Next Update Time {next_update_time}"
                )
            time.sleep(1)
            continue
        except KeyboardInterrupt as ki:
            logging.info(
                f"CoinbaseSocketFeeder : Received KeyboardInterrupt : Shutting Down Gracefully"
            )
            break
        # except Exception as e:
        #     retries += 1
        #     if retries > configs.max_retries:
        #         logging.critical(
        #             f"CoinbaseSocketFeeder : Max Retries Exceeded : Shutting Down : Data {str(e)}"
        #         )
        #         break
        #     logging.error(
        #         f"CoinbaseSocketFeeder : Received Generic Exception : Data {str(e)} : Retry Attempt {retries} of {configs.max_retries}"
        #     )
        #     csf.start()
        #     continue
    csf.close()
