"""
This module provides the price data fetching functionality for the application.

Functions:

    fetch_data(List[str], str) -> Dict[str, Dict[str, float]]

    check_cryptocurrency_existence(str) -> bool

    check_vs_currency_existence(str) -> bool
"""
from typing import Dict, List

import requests

from plotting_tool.constants import PRICES_URL


def fetch_data(
    cryptocurrency_ids: List[str],
    vs_currency: str = "usd"
) -> Dict[str, Dict[str, float]]:
    """Fetch cryptocurrency prices data.

    Args:
        cryptocurrency_ids (List[str]): The ids of cryptocurrencies
        which prices to fetch.
        vs_currency (str): Fiat currency to use for
        comparisons. Defaults to "usd" (US Dollars).

    Returns:
        Union[OPERATION_STATUS, Dict[str, Dict[str, float]]]: Prices of
        cryptocurrencies in fiat currency or None in case fetching was
        unsuccessful.
    """
    # Join the ids of cryptocurrencies to paste it into URL.
    cur_ids_string = "%2C".join(cryptocurrency_ids)

    try:
        response = requests.get(
            PRICES_URL.format(cur_ids_string, vs_currency))
    except requests.exceptions.ConnectionError:
        return None

    if response.status_code == 200 and response.json():
        return response.json()

    return None


def check_cryptocurrency_existence(cryptocurrency_id: str) -> bool:
    """Check whether given cryptocurrency is valid.

    Args:
        cryptocurrency_id (str): The id of cryptocurrency to check.

    Returns:
        bool: True if price data can be fetched, False otherwise.
    """
    # Request data of given currency in USD.
    response = requests.get(PRICES_URL.format(cryptocurrency_id, "usd"))

    # Return true if service responded with 200
    # status code and non-empty payload.
    return response.status_code == 200 and response.json()


def check_vs_currency_existence(vs_currency: str) -> bool:
    """Check whether given vs currency is valid.

    Args:
        vs_currency (str): The code of vs currency.

    Returns:
        bool: True if price data can be fetched using given
        vs currency, False otherwise.
    """
    # Request data of bitcoin in given vs currency
    response = requests.get(PRICES_URL.format("bitcoin", vs_currency))

    # Return true if service responded with 200
    # status code and non-empty payload.
    price = response.json()["bitcoin"]
    return response.status_code == 200 and price
