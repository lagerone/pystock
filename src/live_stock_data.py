import os
import random
from typing import List, Tuple

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


def fetch_live_data(ticker: str) -> Tuple[float, str]:
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
    # PRE or REGULAR
    market_state = json_res["quoteResponse"]["result"][0]["marketState"]
    if market_state == "PRE":
        return (float(json_res["quoteResponse"]["result"][0]["preMarketPrice"]), "PRE")
    if market_state != "REGULAR":
        return (
            float(json_res["quoteResponse"]["result"][0]["postMarketPrice"]),
            "POST",
        )
    return (
        float(json_res["quoteResponse"]["result"][0]["regularMarketPrice"]),
        "REGULAR",
    )


def fetch_fake_live_data():
    return float(random.randint(27, 37))
