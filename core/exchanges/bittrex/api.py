import logging
import asyncio
from hashlib import sha512
from uuid import UUID
from pydantic import ValidationError

from core.enums.http_request_types import HttpRequestType
from core.exchanges.bittrex.models import (
    BittrexBalanceModel,
    BittrexMarketModel,
    BittrexTradeModel,
    BittrexTickerModel,
    BittrexOrderModel,
    BittrexPublicTradeModel,
    BittrexCandleModel,
)
from core.exchanges.bittrex.enums import BittrexCandleLength
from core.exchanges.bittrex.maps import map_bittrex_candle_length
from core.exchanges.bittrex.transformers import transform_trade_bittrex
from core.enums.candle_length import CandleLength
from requests import Session
from requests.exceptions import ConnectionError, ReadTimeout
from typing import Dict
from datetime import datetime, timezone
import hmac
from json.decoder import JSONDecodeError


def get_timestamp():
    return int(
        datetime.now(tz=timezone.utc).timestamp() * 1000
    )  # Must be in Milliseconds, time by default will be in seconds


def get_content_hash(body: str):
    if not isinstance(body, str):
        logging.error(
            f"Get Content Hash : Request Body must be a String : Got {type(body)}"
        )
        return None
    m = sha512()
    encoded_body = body.encode("utf-8")
    m.update(encoded_body)
    return m.hexdigest()


def get_signature(
    api_secret: str, uri: str, timestamp: int, method: str, content_hash: hex
) -> hex:
    value_array = [timestamp, uri, method, content_hash]
    pre_sign = "".join(str(value) for value in value_array)
    return hmac.new(api_secret.encode(), pre_sign.encode(), sha512).hexdigest()


def get_request_url(base_url: str, endpoint: str) -> str:
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    if endpoint.startswith("/"):
        endpoint = endpoint[:-1]
    return f"{base_url}/{endpoint}"


class BittrexApiHelper:
    def __init__(self, exchange):
        self.logger = logging.getLogger("Bottify.BittrexApi")
        self.exchange_id = exchange.id
        self.base_url = exchange.base_url
        self.api_key = exchange.auth.get("api_key")
        self.api_secret = exchange.auth.get("api_secret")
        self.session = Session()
        self.is_ready = False
        self.timeout = 30
        self.sequence_header_name = (
            "Sequence"  # Used for Head requests to return current sequence value
        )

    # TODO Change this to support different accounts for different users somehow
    def set_auth(self, uri, method, body=None):
        self.is_ready = False
        if not self.api_key:
            self.logger.error(
                f"BittrexApiHelpers : Failed to Set Auth Headers : API Key is None"
            )
            return self
        if not body:
            body = ""
        else:
            body = json.dumps(body)
        timestamp = get_timestamp()
        content_hash = get_content_hash(body)
        if not content_hash:
            self.logger.error(
                f"BittrexApiHelpers : Failed to Set Auth Headers : Content Hash is None"
            )
            return self
        signature = get_signature(self.api_secret, uri, timestamp, method, content_hash)
        if not signature:
            self.logger.error(
                f"BittrexApiHelpers : Failed to Sign API Request : Signature is None"
            )
            return self
        self.session.headers.update({"Api-Key": self.api_key})
        self.session.headers.update({"Api-Timestamp": str(timestamp)})
        self.session.headers.update({"Api-Content-Hash": content_hash})
        self.session.headers.update({"Api-Signature": signature})
        self.is_ready = True
        return self

    def make_request(
        self,
        method: str,
        endpoint: str,
        body: Dict = None,
        params: Dict = None,
        use_auth: bool = True,
    ):
        url = get_request_url(self.base_url, endpoint)
        if isinstance(method, HttpRequestType):
            method_str = method.value
        else:
            method_str = method
        if not url:
            self.logger.error(f"Make Request : Request URL is None")
            return None
        if use_auth:
            self.set_auth(url, method, body)

        try:
            response = self.session.request(
                method=method_str,
                url=url,
                data=body,
                timeout=self.timeout,
                params=params,
            )
        except ReadTimeout as rt:
            self.logger.critical(
                f"Make Request : API Operation Timeout : Max Timeout {self.timeout}"
            )
            return None
        if not response.ok:
            self.logger.critical(
                f"Make Request : Response Status Code indicates an Error : Status Code {response.status_code} : Endpoint: {url} : Data {response.text}"
            )
        try:
            if method == HttpRequestType.Head:
                return response.headers
            else:
                return response.json()
        except JSONDecodeError as jde:
            self.logger.critical(
                f"Make Request : JSON Decode Error : {jde} : Data {response.text}"
            )
            return None

    def get_account(self):
        endpoint = "account"
        return self.make_request("GET", endpoint)

    def get_balances(self):
        endpoint = "balances"
        response = self.make_request("GET", endpoint)
        balances = []
        for item in response:
            try:
                balance = BittrexBalanceModel(**item)
                balances.append(balance)
            except ValidationError as ve:
                self.logger.error(
                    f"Bittrex Get Balances : ValidationError : {ve.json()}"
                )
                continue
        if not balances:
            self.logger.error(f"Bittrex Get Balances : No Results")
        return balances

    def get_balance(self, symbol: str):
        endpoint = f"balances/{symbol}"
        response = self.make_request("GET", endpoint)
        try:
            return BittrexBalanceModel(**response)
        except ValidationError as ve:
            self.logger.error(f"Bittrex Get Balance : ValidationError : {ve.json()}")
            return None

    def get_markets(self):
        endpoint = "markets"
        markets = []
        response = self.make_request(method="GET", endpoint=endpoint, use_auth=False)
        if not response:
            self.logger.error(f"Bittrex Get Markets : Response Data Missing or Invalid")
            return markets
        for item in response:
            try:
                market = BittrexMarketModel(**item)
                markets.append(market)
            except ValidationError as ve:
                self.logger.error(
                    f"Bittrex Get Markets : BittrexMarketModel : ValidationError : {ve.json()}"
                )
                continue
        if not markets:
            self.logger.error(f"Bittrex Get Markets : No Results")
        return markets

    def get_trades_by_order(self, source_order_id: UUID, bottify_order_id: UUID):
        endpoint = f"orders/{str(source_order_id)}/executions"
        trades = []
        response = self.make_request(method="GET", endpoint=endpoint)
        for item in response:
            try:
                btx_trade = BittrexTradeModel(**item)
                trade = transform_trade_bittrex(btx_trade, bottify_order_id)
                if not trade:
                    self.logger.error(
                        f"Get Trades by Order : Failed to Transform Trade : Data {btx_trade.json()}"
                    )
                    continue
                trades.append(trade)
            except ValidationError as ve:
                self.logger.error(
                    f"Get Trades by Order : BittrexTradeModel : ValidationError : {ve.json()}"
                )
                continue
        if not trades:
            logging.error("Get Trades by Order : No Results")
        return trades

    def get_executions(
        self,
        market_symbol: str = None,
        limit: int = 200,
        start_date: datetime = None,
        end_date: datetime = None,
    ):
        endpoint - "executions"
        trades = []
        params = {}
        if market_symbol:
            params.update({"marketSymbol": market_symbol})
        if limit:
            params.update({"pageSize": limit})
        if isinstance(start_date, datetime):
            params.update({"startDate": str(start_date.isoformat())})
        if isinstance(end_date, datetime):
            params.udpate({"endDate": str(end_date.isoformat())})
        response = self.make_request(method="GET", endpoint=endpoint, params=params)
        if not response:
            self.logger.error(f"Bittrex Get Trades : Response Data Missing or Invalid")
            return trades
        for item in response:
            try:
                trades.append(BittrexTradeModel(**item))
            except ValidationError as ve:
                self.logger.error(
                    f"Bittrex Get Trades : BittrexTradeModel : ValidationError : {ve.json()}"
                )
                continue
        if not trades:
            self.logger.error(f"Bittrex Get Trades : No Results")
        return trades

    def get_ticker(self, symbol: str):
        if not isinstance(symbol, str):
            self.logger.error(
                f"Get Ticker : Symbol Must be a String : Got {type(symbol)}"
            )
            return None
        endpoint = f"markets/{symbol}/ticker"
        response = self.make_request(method="GET", endpoint=endpoint, use_auth=False)
        if not response:
            self.logger.error("Get Ticker : Invalid API Response")
            return None
        try:
            return BittrexTickerModel(**response)
        except ValidationError as ve:
            self.logger.error(
                f"Get Ticker : BittrexTickerModel : ValidationError : {ve.json()}"
            )
        return None

    def get_order(self, order_source_id: UUID):
        if not isinstance(order_source_id, UUID):
            self.logger.error(
                f"Get Order : Order Source ID Must be a UUID : Got {type(order_source_id)}"
            )
            return None
        endpoint = f"orders/{order_source_id}"
        response = self.make_request(method="GET", endpoint=endpoint)
        if not response:
            self.logger.error("Get Order : Invalid API Response")
            return None
        try:
            return BittrexOrderModel(**response)
        except ValidationError as ve:
            self.logger.error(
                f"Get Order : BittrexOrderModel : ValidationError : {ve.json()}"
            )
            return None

    def generate_public_trades(self, market_symbol: str):
        endpoint = f"markets/{market_symbol}/trades"
        response = self.make_request(method="GET", endpoint=endpoint)
        if not response:
            self.logger.error("Generate Public Trades : Invalid API Response")
            return
        for item in response:
            try:
                yield BittrexPublicTradeModel(market_symbol=market_symbol, **item)
            except ValidationError as ve:
                self.logger.error(
                    f"Generate Public Trades : BittrexTradeModel : ValidationError : {ve.json()} : Data {item}"
                )
                continue
            except TypeError as te:
                self.logger.error(
                    f"Generate Public Trades : BittrexTradeModel : TypeError : {str(te)} :  Type {type(item)} : Data {item}"
                )

    def get_trade_sequence(self, market_symbol: str):
        endpoint = f"markets/{market_symbol}/trades"
        response = self.make_request(
            method=HttpRequestType.Head, endpoint=endpoint, use_auth=False
        )
        if not response:
            self.logger.error("Get Trade Sequence : Invalid API Response")
            return None
        return response.get(self.sequence_header_name)

    def get_ticker_sequence(self):
        endpoint = "markets/tickers"
        response = self.make_request(
            method=HttpRequestType.Head, endpoint=endpoint, use_auth=False
        )
        if not response:
            self.logger.error("Get Ticker Sequence : Invalid API Response")
            return None
        return response.get(self.sequence_header_name)

    def generate_candles(self, symbol: str, length: CandleLength, start: datetime):
        candle_interval = map_bittrex_candle_length(length)
        endpoint = None
        if (
            candle_interval == BittrexCandleLength.OneMinute
            or candle_interval == BittrexCandleLength.FiveMinutes
        ):
            endpoint = f"markets/{symbol}/candles/{candle_interval.value}/historical/{start.year}/{start.month}/{start.day}"
        elif candle_interval == BittrexCandleLength.OneHour:
            endpoint = f"markets/{symbol}/candles/{candle_interval.value}/historical/{start.year}/{start.month}"
        elif candle_interval == BittrexCandleLength.OneDay:
            endpoint = f"markets/{symbol}/candles/{candle_interval.value}/historical/{start.year}"
        else:
            self.logger.error(
                f"Bittrex Generate Candles : Invalid Length : Got {str(length)}"
            )
            return
        response = self.make_request(
            method=HttpRequestType.Get, endpoint=endpoint, use_auth=False
        )
        if not response:
            self.logger.error("Bittrex Generate Candles : Invalid API Response")
            return None
        for item in response:
            try:
                yield BittrexCandleModel(
                    exchange_id=self.exchange_id,
                    market_symbol=symbol,
                    length=length,
                    **item,
                )
            except ValidationError as ve:
                self.logger.error(
                    f"Bittrex Generate Candles : ValidationError : BittrexCandleModel : {ve.json()}"
                )
                continue
