import cbpro
import time
import logging
import requests
from core.elasticsearch.api import ElasticApiHelper
from core.enums.statuses import BottifyStatus
from core.exchanges.coinbase.models import (
    CoinbaseSocketTickerModel,
    CoinbaseSocketFeederConfig,
)
from core.models.market import MarketModel
from pydantic import ValidationError


class CoinbaseSocketFeeder(cbpro.WebsocketClient):
    def __init__(self, *args, **kwargs):
        configs = kwargs.pop("configs")
        if not configs:
            logging.error(f"Init : Config is Missing or Invalid")
            return
        try:
            self.configs = CoinbaseSocketFeederConfig.parse_raw(configs)
        except ValidationError as ve:
            logging.error(
                f"Init : CoinbaseSocketFeederConfig : ValidationError : {ve.json()}"
            )
            return
        self.markets = []
        kwargs.update({"channels": self.configs.channels})
        super(CoinbaseSocketFeeder, self).__init__(*args, **kwargs)

    def set_products(self):
        self.products = []
        endpoint = f"{self.configs.products_url}/{self.configs.exchange_id}"
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

    def on_open(self):
        if not self.configs:
            logging.error(f"Startup Error : Config is Missing or Invalid")
            return
        self.url = self.configs.socket_url
        self.elastic = ElasticApiHelper()
        self.set_products()

    def on_message(self, message):
        message_type = message.pop("type")
        if message_type == "ticker":
            model = CoinbaseSocketTickerModel(**message)
            index_name = self.configs.ticker_index_name
            if not index_name:
                logging.error(
                    "Message Handler : Required Config 'ticker_index_name' Not Provided"
                )
                return
            self.elastic.index_one(index_name, None, model.json())
        else:
            print(f"Message Type: {message_type}")
            print(f"Message: {message}")

    def run(self):
        pass
