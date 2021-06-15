import logging
import os
import sys
from datetime import datetime, timezone
from typing import List

import termplotlib as tpl
import yfinance as yf

from app_config import TICKER_DATA_PATH
from live_stock_data import (
    MarketType,
    append_data_to_file,
    fetch_live_data,
    read_live_data_file,
)

_LOG_LEVEL = int(os.getenv("LOG_LEVEL", f"{logging.ERROR}"))
logging.basicConfig(level=_LOG_LEVEL)


def _create_ticker_data_file(ticker: str, cache_key: str) -> str:
    os.makedirs(TICKER_DATA_PATH, exist_ok=True)
    file_path = os.path.join(TICKER_DATA_PATH, f"ticker_{ticker}_{cache_key}.csv")
    if not os.path.isfile(file_path):
        data = yf.download(tickers=ticker, period="20d", progress=False)
        data.to_csv(file_path)
    return file_path


def _read_ticker_data_file(file_path: str) -> List[str]:
    with open(file_path, "r") as reader:
        lines = reader.readlines()
    return lines


class TColor:
    GREEN = "\033[32m"
    RED = "\033[31m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def _get_file_cache_key():
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def _create_graph_prices(ticker: str):
    live_data_file_path = os.path.join(
        f"{TICKER_DATA_PATH}", f"ticker_{ticker}_live_{_get_file_cache_key()}"
    )
    live_data_count = 100
    live_stock_data = fetch_live_data(ticker=ticker)
    live_stock_price = live_stock_data.get_live_stock_price()

    live_graph_price = int(live_stock_price.market_price * 100)
    stored_prices = read_live_data_file(file_path=live_data_file_path)
    is_stock_live = stored_prices[-3:] != [
        live_graph_price,
        live_graph_price,
        live_graph_price,
    ]
    if is_stock_live:
        append_data_to_file(file_path=live_data_file_path, live_price=live_graph_price)
    graph_prices = (
        stored_prices[-live_data_count:]
        if len(stored_prices) > live_data_count
        else stored_prices
    )
    graph_prices.append(live_graph_price)
    return graph_prices


def _is_stock_live(stored_prices: List[int], live_stock_price: float):
    live_graph_price = int(live_stock_price * 100)
    return stored_prices[-3:] != [
        live_graph_price,
        live_graph_price,
        live_graph_price,
    ]


# pylint: disable=too-many-locals
def _render_live_data_graph(ticker: str, prices: List[float], show_graph: bool):
    live_data_file_path = os.path.join(
        f"{TICKER_DATA_PATH}", f"ticker_{ticker}_live_{_get_file_cache_key()}"
    )
    live_stock_data = fetch_live_data(ticker=ticker)
    live_stock_price = live_stock_data.get_live_stock_price()

    closing_stock_price: float = (
        live_stock_data.regular_market_price.market_price
        if live_stock_data.market_type != MarketType.REGULAR
        else live_stock_data.regular_market_previous_close
    )
    graph_prices = _create_graph_prices(ticker)

    def ensure_two_dec(num: float) -> str:
        return "{:.2f}".format(num)

    previous_price_delta = prices[-1] - prices[-2]

    stored_prices = read_live_data_file(file_path=live_data_file_path)
    is_stock_live = _is_stock_live(
        stored_prices=stored_prices, live_stock_price=live_stock_price.market_price
    )

    change_color = TColor.GREEN if live_stock_price.market_change > 0 else TColor.RED
    live_color = TColor.GREEN if is_stock_live else ""
    live_color_end = TColor.END if is_stock_live else ""
    close_change_color = TColor.GREEN if previous_price_delta >= 0 else TColor.RED

    market_type_map = {
        MarketType.PREPRE.value: "PREPRE".rjust(7, " "),
        MarketType.PRE.value: "PRE".rjust(7, " "),
        MarketType.REGULAR.value: "REGULAR",
        MarketType.POST.value: "POST".rjust(7, " "),
        MarketType.CLOSED.value: "CLOSED".rjust(7, " "),
    }

    print(
        f"  {live_color}{TColor.BOLD}{ticker.ljust(3, ' ')}{TColor.END}{live_color_end}"
        f"   {market_type_map[live_stock_data.market_type]}"
        f"     {TColor.BOLD}{ensure_two_dec(live_stock_price.market_price)}{TColor.END}"
        f"     {change_color}{ensure_two_dec(live_stock_price.market_change)}"
        f"     ({ensure_two_dec(live_stock_price.market_change_percent)}%){TColor.END}"
    )
    print(
        f"  CLOSED          "
        f"  {ensure_two_dec(closing_stock_price)}"
        f"     {close_change_color}{ensure_two_dec(previous_price_delta)}{TColor.END}"
    )
    print(
        f"  PREVCLOSE       "
        f"  {ensure_two_dec(live_stock_data.regular_market_previous_close)}"
    )
    print("")
    if show_graph:
        live_fig = tpl.figure()
        live_fig.plot(range(len(graph_prices) + 1), graph_prices, width=50)
        live_fig.show()


# pylint: enable=too-many-locals


def _render_ticker(ticker: str, show_graph: bool = True) -> None:
    ticker_file_path = _create_ticker_data_file(
        ticker=ticker, cache_key=_get_file_cache_key()
    )
    lines = _read_ticker_data_file(file_path=ticker_file_path)

    day_counter = -20
    days: List[int] = []
    prices: List[float] = []
    for line in lines[1:]:
        days.append(day_counter)
        day_counter += 1
        prices.append(float(line.split(",")[4]))

    _render_live_data_graph(ticker=ticker, prices=prices, show_graph=show_graph)

    if show_graph:
        close_price_fig = tpl.figure()
        close_price_fig.plot(days, prices, width=50)
        print("\n")
        print("      Closing prices, last 20 days.")
        close_price_fig.show()


def _main(tickers=List[str]):
    for ticker in tickers:
        logging.debug(f"Rendering ticker {ticker}...")
        _render_ticker(ticker=ticker, show_graph=len(tickers) == 1)
        print("\n")


if __name__ == "__main__":
    _main(tickers=sys.argv[1:] if len(sys.argv) > 1 else [os.environ["DEFAULT_TICKER"]])
