import os
import random
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

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
class LiveStockData:
    pre_market_price: float
    pre_market_change: float
    pre_market_change_percent: float
    regular_market_price: float
    regular_market_change: float
    regular_market_change_percent: float
    regular_market_previous_close: float
    post_market_price: float
    post_market_change: float
    post_market_change_percent: float
    market_type: Literal["PRE", "REGULAR", "POST"]

    def get_live_stock_price(self) -> Tuple[float, float, float]:
        if self.market_type == "REGULAR":
            return (
                self.regular_market_price,
                self.regular_market_change,
                self.regular_market_change_percent,
            )

        if self.market_type == "PRE":
            return (
                self.pre_market_price,
                self.pre_market_change,
                self.pre_market_change_percent,
            )

        return (
            self.post_market_price,
            self.post_market_change,
            self.post_market_change_percent,
        )


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
        pre_market_price=float(data.get("preMarketPrice", 0)),
        pre_market_change=float(data.get("preMarketChange", 0)),
        pre_market_change_percent=float(data.get("preMarketChangePercent", 0)),
        regular_market_price=float(data["regularMarketPrice"]),
        regular_market_change=float(data["regularMarketChange"]),
        regular_market_change_percent=float(data["regularMarketChangePercent"]),
        regular_market_previous_close=float(data["regularMarketPreviousClose"]),
        post_market_price=float(data.get("postMarketPrice", 0)),
        post_market_change=float(data.get("postMarketChange", 0)),
        post_market_change_percent=float(data.get("postMarketChangePercent", 0)),
        market_type=data["marketState"],
    )


def fetch_fake_live_data():
    return float(random.randint(27, 37))
