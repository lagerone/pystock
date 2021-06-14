import os
import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

import requests


def append_data_to_file(file_path: str, live_price: int) -> None:
    with open(file_path, "a+") as file:
        # Move read cursor to the start of file.
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        # Append text at the end of file
        file.write(str(live_price))


def read_live_data_file(file_path: str) -> List[int]:
    lines = []
    file_mode = "r" if os.path.isfile(file_path) else "w+"
    with open(file_path, file_mode) as file:
        lines = file.readlines()
    return [int(line) for line in lines]


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class MarketPrice:
    market_price: float
    market_change: float
    market_change_percent: float


class MarketType(str, Enum):
    PRE = "PRE"
    REGULAR = "REGULAR"
    POST = "POST"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class LiveStockData:
    pre_market_price: MarketPrice
    regular_market_price: MarketPrice
    regular_market_previous_close: float
    post_market_price: MarketPrice
    market_type: MarketType

    def _get_live_stock_price(self) -> MarketPrice:
        if self.market_type == "CLOSED" and self.post_market_price.market_change > 0:
            return self.post_market_price
        if self.market_type == "REGULAR":
            return self.regular_market_price
        if self.market_type == "PRE":
            return self.pre_market_price
        return self.post_market_price

    def get_live_stock_price(self) -> MarketPrice:
        live_stock_price = self._get_live_stock_price()
        # logging.debug(f"live_stock_price: {live_stock_price}")
        return live_stock_price


# pylint: enable=too-many-instance-attributes


def fetch_live_data(ticker: str) -> LiveStockData:
    # stock price (float), market name (str), e.g. "POST", "PRE", "REGULAR"
    api_end_point = (
        "https://query1.finance.yahoo.com/v7/"
        "finance/quote?lang=en-US&region=US&corsDomain=finance.yahoo.com"
    )
    fields = [
        "symbol",
        "marketState",
        "regularMarketPrice",
        "regularMarketChange",
        "regularMarketChangePercent",
        "preMarketPrice",
        "preMarketChange",
        "preMarketChangePercent",
        "postMarketPrice",
        "postMarketChange",
        "postMarketChangePercent",
    ]
    url = f"{api_end_point}&fields={','.join(fields)}&symbols={ticker}"
    res = requests.get(url)
    json_res = res.json()

    data: Dict = json_res["quoteResponse"]["result"][0]
    return LiveStockData(
        pre_market_price=_market_factory(market_type=MarketType.PRE, data=data),
        regular_market_price=_market_factory(market_type=MarketType.REGULAR, data=data),
        post_market_price=_market_factory(market_type=MarketType.POST, data=data),
        regular_market_previous_close=float(data.get("regularMarketPreviousClose", 0)),
        market_type=MarketType[data["marketState"]],
    )


def _market_factory(market_type: MarketType, data: Dict):
    market_key = market_type.lower()
    return MarketPrice(
        market_price=float(data.get(f"{market_key}MarketPrice", 0)),
        market_change=float(data.get(f"{market_key}MarketChange", 0)),
        market_change_percent=float(data.get(f"{market_key}MarketChangePercent", 0)),
    )


def fetch_fake_live_data():
    return float(random.randint(27, 37))
