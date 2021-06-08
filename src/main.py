import os
import sys
from datetime import datetime, timezone
from typing import List, Tuple

import termplotlib as tpl
import yfinance as yf

from live_stock_data import append_data_to_file, fetch_live_data, read_live_data_file


def _create_ticker_data_file(ticker: str, cache_key: str) -> str:
    file_path = f"ticker_data/ticker_{ticker}_{cache_key}.csv"
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


def _render_live_data_graph(ticker: str):
    cache_key = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    live_data_file_path = f"ticker_data/ticker_{ticker}_live_{cache_key}"
    live_data_count = 100
    live_stock_price, market_type = fetch_live_data(ticker=ticker)
    live_graph_price = int(live_stock_price * 100)
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

    live_fig = tpl.figure()
    live_fig.plot(range(len(graph_prices) + 1), graph_prices, width=50)
    live_text = (
        f"{TColor.BOLD}{TColor.GREEN}• live{TColor.END}{TColor.END}"
        if is_stock_live
        else ""
    )
    print(f"        Market: {market_type} {live_text}")
    live_fig.show()


def _calc_streak_days(prices: List[float]) -> Tuple[int, int]:
    reversed_prices = list(reversed(prices))

    winning = 0
    losing = 0
    prev_price = reversed_prices[0]
    for current_price in reversed_prices[1:]:
        if current_price < prev_price:
            if losing:
                break
            winning += 1
        if current_price > prev_price:
            if winning:
                break
            losing += 1
        prev_price = current_price
    return (winning, losing)


def _main(ticker: str) -> None:
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

    close_price_fig = tpl.figure()
    close_price_fig.plot(days, prices, width=50)

    _render_live_data_graph(ticker=ticker)

    price_delta = prices[-1] - prices[-2]

    delta_symbol = "+" if price_delta >= 0 else "-"
    price_delta = f"{delta_symbol}{round(price_delta, 2)}"

    print("\n")

    print(f"      {TColor.BOLD}{ticker}{TColor.END} closing prices, last 20 days.")
    print(
        f"      Closed yesterday at {TColor.BOLD}{prices[-1]} ({price_delta}){TColor.END}."
    )

    winning_streak, losing_streak = _calc_streak_days(prices=prices)
    if winning_streak > 1 or losing_streak > 1:
        streak_days = winning_streak if winning_streak else losing_streak
        streak_type = "winning" if winning_streak else "losing"
        t_color = TColor.GREEN if winning_streak else TColor.RED
        print(
            f"      On a {t_color}{streak_days} day {streak_type} streak{TColor.END}."
        )
    elif winning_streak or losing_streak:
        streak_type = "winning" if winning_streak else "losing"
        emoji = "☹" if losing_streak else "☺"
        t_color = TColor.GREEN if winning_streak else TColor.RED
        print(
            f"      {t_color}{emoji}{TColor.END} "
            f" Today is a "
            f"{t_color}{TColor.BOLD}{streak_type}{TColor.END}{TColor.END}"
            " day."
        )
    close_price_fig.show()


if __name__ == "__main__":
    _main(ticker=sys.argv[1] if len(sys.argv) > 1 else os.environ["DEFAULT_TICKER"])
