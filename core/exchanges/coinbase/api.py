import logging
import asyncio
import codecs
import base64
import time
from uuid import UUID
from hashlib import sha256
from cbpro import AuthenticatedClient
from pydantic import ValidationError
from core.enums.candle_length import CandleLength
from core.exchanges.coinbase.enums import CoinbaseOrderStatus
from core.config import COINBASE_BASE_URL, COINBASE_API_TIMEOUT_SECONDS
from core.exchanges.coinbase.models import (
    CoinbaseBalanceModel,
    CoinbaseMarketModel,
    CoinbaseTradeModel,
    CoinbaseOrderModel,
    CoinbaseApiTickerModel,
    CoinbasePublicTradeModel,
    CoinbaseDailyCurrencyStatModel,
    CoinbaseCandleModel,
)
from core.exchanges.coinbase.transformers import (
    transform_order_create_to_coinbase,
    transform_coinbase_order,
    transform_trade_coinbase,
)
from core.exchanges.coinbase.maps import map_coinbase_candle_length
from requests import Session
from requests.exceptions import ConnectionError, ReadTimeout
from requests.auth import AuthBase
from typing import Dict, List
from datetime import datetime, timezone, timedelta
import hmac
from json.decoder import JSONDecodeError


def get_timestamp():
    return int(datetime.now(tz=timezone.utc).timestamp())


# Create custom authentication for Exchange, from https://docs.pro.coinbase.com/?python#creating-a-request
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        logging.debug(f"CoinbaseExchangeAuth Timestamp : {timestamp}")
        array = [
            timestamp,
            request.method,
            request.path_url,
            request.body if request.body else "",
        ]
        message = "".join(str(value) for value in array)
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), sha256)
        signature_raw = signature.hexdigest()
        signature_b64 = (
            codecs.encode(codecs.decode(signature_raw, "hex"), "base64")
            .decode()
            .rstrip("\n")
        )

        request.headers.update(
            {
                "CB-ACCESS-SIGN": signature_b64,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "CB-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json",
            }
        )
        return request


class CoinbaseApiHelper:
    def __init__(self, exchange):
        self.logger = logging.getLogger("Bottify.CoinbaseApi")
        self.exchange_id = exchange.id
        self.base_url = exchange.base_url
        self.api_key = exchange.auth.get("api_key")
        if not self.api_key:
            self.logger.error(f"API Key is None : Required Key is 'api_key'")
            return
        self.api_secret = exchange.auth.get("api_secret")
        if not self.api_secret:
            self.logger.error(f"API Secret is None : Required Key is 'api_secret'")
            return
        self.api_passphrase = exchange.auth.get("api_passphrase")
        if not self.api_passphrase:
            self.logger.error(
                f"API Passphrase is None : Required Key is 'api_passphrase'"
            )
            return
        self.timeout = COINBASE_API_TIMEOUT_SECONDS
        self.session = Session()
        self.client = AuthenticatedClient(
            self.api_key, self.api_secret, self.api_passphrase, api_url=self.base_url
        )
        self.candle_request_limit = 300  # API requests fail if we try to get more than 300 candles, may change in future

    def set_auth(self):
        return CoinbaseExchangeAuth(self.api_key, self.api_secret, self.api_passphrase)

    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        body: Dict = None,
        use_auth: bool = True,
    ):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=body,
                auth=self.set_auth() if use_auth else None,
                timeout=self.timeout,
            )
        except ReadTimeout as rt:
            self.logger.error(
                f"Coinbase Make Request : API Operation Timeout : Max Timeout {self.timeout}"
            )
            return None
        if not response.ok:
            self.logger.error(
                f"Make Request : Response Status Code indicates an Error : Status Code {response.status_code} : Data {response.text}"
            )
            return None
        try:
            return response.json()
        except JSONDecodeError as jde:
            self.logger.error(
                f"Make Request : JSON Decode Error : {jde} : Data {response.text}"
            )
            return None

    def get_account(self):
        endpoint = "accounts"
        return self.make_request("GET", endpoint)

    def get_balances(self):
        endpoint = "accounts"
        balances = []
        response = self.make_request("GET", endpoint)

        if not response:
            self.logger.error(
                f"Coinbase Get Balances : API Call Returned No Data : Balance Update Failed"
            )
            return balances

        for item in response:
            try:
                if not isinstance(item, dict):
                    self.logger.error(
                        f"Coinbase Get Balances : Balance Item is not a Dict : Type {type(item)} : Value {item}"
                    )
                    continue
                balance = CoinbaseBalanceModel(**item)
                balances.append(balance)
            except ValidationError as ve:
                self.logger.error(
                    f"Coinbase Get Balances : ValidationError : {ve.json()}"
                )
                continue
        if not balances:
            self.logger.error(f"Coinbase Get Balances : No Results")
        return balances

    def get_balance(self, symbol: str):
        endpoint = f"balances/{symbol}"
        response = self.make_request("GET", endpoint)
        try:
            return CoinbaseBalanceModel(**response)
        except ValidationError as ve:
            self.logger.error(f"Coinbase Get Balance : ValidationError : {ve.json()}")
            return None

    def get_markets(self):
        endpoint = "products"
        markets = []
        response = self.make_request(method="GET", endpoint=endpoint, use_auth=False)
        if not response:
            logging.error(
                f"Coinbase Get Markets : API Call Returned No Data : Market Update Failed"
            )
            return markets
        for item in response:
            try:
                markets.append(CoinbaseMarketModel(**item))
            except ValidationError as ve:
                logging.error(
                    f"Coinbase Get Markets : CoinbaseMarketModel : ValidationError : {ve.json()} \n Data: {item}"
                )
                continue
        if not markets:
            logging.error(f"Coinbase Get Markets : No Results")
        return markets

    def get_orders(self, status: CoinbaseOrderStatus = None, market_symbol: str = None):
        orders = []
        endpoint = "orders"
        params = {}
        if status:
            if isinstance(status, CoinbaseOrderStatus):
                params.update({"status": status.value})
        if market_symbol:
            params.update({"product_id": market_symbol})
        response = self.make_request("GET", endpoint, params)
        if not response:
            self.logger.error(f"Coinbase Get Orders : Invalid API Response")
            return orders
        for item in response:
            try:
                order = CoinbaseOrderModel(exchange_id=self.exchange_id, **item)
                orders.append(order)
            except ValidationError as ve:
                self.logger.error(
                    f"Coinbase Get Orders : CoinbaseOrderModel : ValidationError : {ve.json()}"
                )
                continue
        if not orders:
            self.logger.error(f"Coinbase Get Orders : No Results")
        return orders

    def get_trades(
        self, market_symbol: str = None, order_source_id: str = None
    ) -> List[CoinbaseTradeModel]:  # Coinbase Calls these "Fills"
        trades = []
        params = {}
        endpoint = "fills"
        if not market_symbol and not order_source_id:
            self.logger.error(
                f"Coinbase Get Trades : One of Market Symbol or Order Source ID params is Required"
            )
            return trades
        if order_source_id:
            params.update({"order_source_id": order_source_id})
        elif market_symbol:
            params.update({"product_id": market_symbol})
        else:
            self.logger.error(f"Coinbase Get Trades : Invalid Input Parameters")
            return trades
        response = self.make_request(method="GET", endpoint=endpoint, params=params)
        if not response:
            self.logger.error(f"Coinbase Get Trades : Invalid API Response")
            return trades
        for item in response:
            try:
                trades.append(CoinbaseTradeModel(exchange_id=self.exchange_id, **item))
            except ValidationError as ve:
                self.logger.error(
                    f"Coinbase Get Trades : CoinbaseTradeModel : ValidationError : {ve.json()}"
                )
                continue
        if not trades:
            self.logger.error(f"Coinbase Get Trades : No Results")
        return trades

    def place_order(self, order_in, market_symbol):
        endpoint = "orders"
        cb_order = transform_order_create_to_coinbase(order_in, market_symbol)
        if not cb_order:
            self.logger.error(
                f"Coinbase Place Order : Failed to Transform Bottify Order to Coinbase Order"
            )
            return
        self.logger.info(
            f"Coinbase Place Order : Data {cb_order.json(exclude_none=True)}"
        )
        response = self.make_request(
            "POST", endpoint, body=cb_order.json(exclude_none=True)
        )
        if not response:
            self.logger.error("Coinbase Place Order : Invalid API Response")
            return
        try:
            exchange_order = CoinbaseOrderModel(
                exchange_id=self.exchange_id, **response
            )
            return transform_coinbase_order(
                exchange_order,
                order_in.strategy_id,
                order_in.market_id,
                order_in.order_guid,
            )
        except ValidationError as ve:
            self.logger.error(
                f"Coinbase Place Order : CoinbaseOrderModel : ValidationError : {ve.json()}"
            )
            return None

    def get_ticker(self, symbol: str):
        if not isinstance(symbol, str):
            self.logger.error(
                f"Coinbase Get Ticker : Symbol Must be a String : Got {type(symbol)}"
            )
        endpoint = f"products/{symbol}/ticker"
        response = self.make_request("GET", endpoint, use_auth=False)
        if not response:
            self.logger.error("Get Ticker : Invalid API Response")
            return
        try:
            return CoinbaseApiTickerModel(**response)
        except ValidationError as ve:
            self.logger.error(
                f"Get Ticker : CoinbaseTickerModel : ValidationError : {ve.json()}"
            )
        return None

    def get_order(self, order_in):
        endpoint = f"orders/{order_in.source_id}"
        response = self.make_request(method="GET", endpoint=endpoint)
        if not response:
            self.logger.error("Get Order : Invalid API Response")
            return None
        try:
            cb_order = CoinbaseOrderModel(**response)
            return transform_coinbase_order(
                cb_order,
                order_in.strategy_id,
                order_in.market_id,
                order_in.order_guid,
            )
        except ValidationError as ve:
            self.logger.error(
                f"Get Order : CoinbaseOrderModel : ValidationError : {ve.json()}"
            )
            return None

    def get_trades_by_order(self, source_order_id: UUID, bottify_order_id: UUID):
        endpoint = "fills"
        params = {"order_id": str(source_order_id)}
        trades = []
        response = self.make_request(method="GET", endpoint=endpoint, params=params)
        for item in response:
            try:
                cb_trade = CoinbaseTradeModel(**item)
                trade = transform_trade_coinbase(cb_trade, bottify_order_id)
                if not trade:
                    self.logger.error(
                        f"Get Trades by Order : Failed to Transform Trade : Data {cb_trade.json()}"
                    )
                    continue
                trades.append(trade)
            except ValidationError as ve:
                self.logger.error(
                    f"Get Trades by Order : CoinbaseTradeModel : ValidationError : {ve.json()}"
                )
                continue
        if not trades:
            logging.error("Get Trades by Order : No Results")
        return trades

    def generate_public_trades(
        self, symbol: str, before: int = None, after: int = None, limit: int = None
    ):
        trades = []
        params = {}
        if before:
            params.update({"before": before})
        if after:
            params.update({"after": after})
        if limit:
            params.update({"limit": limit})
        endpoint = f"products/{symbol}/trades"
        response = self.make_request("GET", endpoint, params)
        if not response:
            self.logger.error(
                f"Coinbase Public Trade Generator : Invalid API Response : Endpoint {endpoint} : Params {params}"
            )
            return
        for trade_data in response:
            try:
                yield CoinbasePublicTradeModel(market_symbol=symbol, **trade_data)

            except ValidationError as ve:
                self.logger.error(
                    f"Get Public Trades : CoinbasePublicTradeModel : ValidationError : {ve.json()}"
                )
                continue
            except TypeError as te:
                self.logger.error(
                    f"Get Public Trades : CoinbasePublicTradeModel : TypeError : {str(te)} : Trade Data {trade_data}"
                )
                continue

    def get_daily_currency_stats(self, symbol: str):
        if not isinstance(symbol, str):
            self.logger.error(
                f"Generate Daily Currency Stats : Symbol Input Must be a String : Got {type(symbol)}"
            )
            return None
        stat = self.client.get_product_24hr_stats(product_id=symbol)
        try:
            return CoinbaseDailyCurrencyStatModel(**stat)
        except ValidationError as ve:
            self.logger.error(
                f"Generate Daily Currency Stats : CoinbaseDailyCurrencyStatModel : ValidationError : {ve.json()} : Data {stat}"
            )
        except TypeError as te:
            self.logger.error(
                f"Get Daily Currency Stats : CoinbaseDailyCurrencyStatModel : TypeError : {str(te)} : Trade Data {stat}"
            )
        return None

    def generate_candles(self, symbol: str, length: CandleLength, start: datetime):
        granularity = map_coinbase_candle_length(length)
        if not granularity:
            self.logger.error(
                f"Coinbase Generate Candles : Invalid Candle Length : Value {str(length)}"
            )
            return
        max_interval_seconds = self.candle_request_limit * granularity.value
        end = start + timedelta(seconds=max_interval_seconds)
        for item in self.client.get_product_historic_rates(
            symbol, start=start, end=end, granularity=granularity.value
        ):
            if len(item) == 6:
                try:
                    yield CoinbaseCandleModel(
                        exchange_id=self.exchange_id,
                        market_symbol=symbol,
                        length=length,
                        time=item[0],
                        low=item[1],
                        high=item[2],
                        open=item[3],
                        close=item[4],
                        volume=item[5],
                    )
                except ValidationError as ve:
                    self.logger.error(
                        f"Coinbase Generate Candles : ValidationError : CoinbaseCandleModel : {ve.json()}"
                    )
                    continue
            else:
                logging.error(
                    f"Coinbse Generate Candles : Response Item has Invalid Length : Required 6 : Got {len(item)} : Data {item}"
                )
                continue
        return
