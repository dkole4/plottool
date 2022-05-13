"""
This module provides file handling functionality for the application.

Functions:

    ensure_data_files_existence()

    load_cryptocur_prices(Optional[List[str]])
    -> Dict[str, Union[List[float], List[datetime]]]

    load_cryptocur_statistics(Optional[List[str]])
    -> Dict[str, Dict[str, float]]

    calculate_plotting_point_ratio() -> int

    load_cryptocur_plot_prices(Optional[List[str]])
    -> Dict[str, Union[List[float], List[datetime]]]

    load_bundle_plot_prices(Optional[List[str]])
    -> Dict[str, Union[List[float], List[datetime]]]

    get_csv_line_count(str) -> int

    load_bundles() -> Dict[str, List[str]]

    load_bundle_ids() -> List[str]

    load_bundle(str) -> Dict[str, float]

    valid_bundle_ids(List[str]) -> bool

    create_bundle(str)

    add_cryptocur_to_bundle(str, str, int)

    remove_cryptocur_from_bundle(str, str)

    delete_bundle(str)

    exists_in_bundles(str) -> bool

    load_cryptocurrency_ids() -> List[str]

    valid_cryptocurrency_ids(List[str]) -> bool

    add_new_cryptocurrency(str) -> List[str]

    remove_cryptocurrency(str) -> List[str]

    write_cryptocur_prices_entry(
        Dict[str, Union[datetime, float]], Optional[List[str]])

    convert_prices(float)
"""
from itertools import zip_longest
import os
import csv
import json
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from plotting_tool.constants import (
    DATA_FOLDER, TMP_FILEPATH,
    IDS_FILEPATH, IDS_DEFAULT_STATE,
    PRICES_FILEPATH, PRICES_DEFAULT_STATE,
    BUNDLES_FILEPATH, BUNDLES_DEFAULT_STATE,
    BUNDLE_PRICES_FILEPATH, BUNDLE_PRICES_DEFAULT_STATE
)


def _read_csv(filename: str) -> Generator[Dict[str, str], None, None]:
    with open(filename, "r", encoding="utf-8") as csvinput:
        reader = csv.DictReader(csvinput)
        yield from reader


def ensure_data_files_existence() -> None:
    """
    Ensure the existence of data files needed for the application.
    """
    # Create data directory if not found.
    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)

    # Create and write default state to the data files if not found.
    for file_path, default_state in (
        (IDS_FILEPATH, IDS_DEFAULT_STATE),
        (PRICES_FILEPATH, PRICES_DEFAULT_STATE),
        (BUNDLES_FILEPATH, BUNDLES_DEFAULT_STATE),
        (BUNDLE_PRICES_FILEPATH, BUNDLE_PRICES_DEFAULT_STATE)
    ):
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                if isinstance(default_state, str):
                    file.write(default_state)
                else:
                    file.write(json.dumps(default_state))


def load_cryptocur_prices(
    cryptocurrency_ids: Optional[List[str]] = None
) -> Dict[str, Union[List[float], List[datetime]]]:
    """Read cryptocurrency prices file.

    Args:
        cryptocurrency_ids (Optional[List[str]], optional): The ids of
        cryptocurrencies which prices to load. Defaults to None.

    Returns:
        Dict[str, Union[List[float], List[datetime]]]: Timestamps and
        prices of currencies.
    """
    # Set cryptocurrency_ids to all existing if none
    # was passed to the function.
    if not cryptocurrency_ids:
        cryptocurrency_ids = load_cryptocurrency_ids()

    prices = {cur_id: [] for cur_id in cryptocurrency_ids}
    prices["timestamp"] = []

    num = 0
    for row in _read_csv(PRICES_FILEPATH):
        prices["timestamp"].append(datetime.fromisoformat(row["timestamp"]))
        for cur_id in cryptocurrency_ids:
            num = float(row[cur_id])
            if num > 0:
                prices[cur_id].append(num)

    return prices


def load_cryptocur_statistics(
    cryptocurrency_ids: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """Read cryptocurrency prices and calculate statistics based on read data.

    Args:
        cryptocurrency_ids (Optional[List[str]], optional): The ids of
        cryptocurrencies which statistics to calculate. Defaults to None.

    Returns:
        Dict[str, Dict[str, float]]: Calculated statistics of cryptocurrencies.
    """
    # Set cryptocurrency_ids to all existing if none
    # was passed to the function.
    if not cryptocurrency_ids:
        cryptocurrency_ids = load_cryptocurrency_ids()

    # Sum and count of all prices
    price_sums = {cur: [0, 0] for cur in cryptocurrency_ids}

    # Overall stats, using 100,000,000 as the initial min value
    stats = {
        cur_id: {"min": 100000000, "max": 0} for cur_id in cryptocurrency_ids
    }

    num = 0
    for row in _read_csv(PRICES_FILEPATH):
        for cur_id in cryptocurrency_ids:
            num = float(row[cur_id])
            if num == 0:
                continue

            price_sums[cur_id][0] += num
            price_sums[cur_id][1] += 1

            if num > stats[cur_id]["max"]:
                stats[cur_id]["max"] = num
            if num < stats[cur_id]["min"]:
                stats[cur_id]["min"] = num

    for cur, price_sum in price_sums.items():
        # Set mean and min to 0 if no prices available
        # for a currency, otherwise calculate mean.
        if price_sum[1] == 0:
            stats[cur]["mean"] = 0
            stats[cur]["min"] = 0
        else:
            stats[cur]["mean"] = price_sum[0] / price_sum[1]

    return stats


def calculate_plotting_point_ratio() -> int:
    """Calculate the ratio of prices to load for faster plotting.

    Returns:
        int: The ratio to use in reading prices.
    """
    prices_line_count = get_csv_line_count(PRICES_FILEPATH)

    # Using 0-1999 range for the maximum number of points.
    if prices_line_count >= 2000:
        return prices_line_count // 1000

    return 1


def load_cryptocur_plot_prices(
    cryptocurrency_ids: Optional[List[str]] = None
) -> Dict[str, Union[List[float], List[datetime]]]:
    """Load cryptocurrency prices for plotting.

    Args:
        cryptocurrency_ids (Optional[List[str]], optional): The ids of
        cryptocurrencies which prices to load. Defaults to None.

    Returns:
        Dict[str, Union[List[float], List[datetime]]]: The prices of
        requested cryptocurrencies.
    """
    # Set cryptocurrency_ids to all existing if
    # none was passed to the function.
    if not cryptocurrency_ids:
        cryptocurrency_ids = load_cryptocurrency_ids()

    return _load_plotting_prices(PRICES_FILEPATH, cryptocurrency_ids)


def load_bundle_plot_prices(
    bundle_ids: Optional[List[str]] = None
) -> Dict[str, Union[List[float], List[datetime]]]:
    """Load bundle prices for plotting.

    Args:
        bundle_ids (Optional[List[str]], optional): The ids of bundles
        which prices to load. Defaults to None.

    Returns:
        Dict[str, Union[List[float], List[datetime]]]: The prices of
        requested bundles.
    """
    # Set bundle_ids to all existing if none was passed to the function.
    if not bundle_ids:
        bundle_ids = load_bundle_ids()

    return _load_plotting_prices(BUNDLE_PRICES_FILEPATH, bundle_ids)


def _load_plotting_prices(
    filename: str, columns: List[str]
) -> Tuple[Dict[str, Union[List[float], List[datetime]]], float, float]:
    point_ratio = calculate_plotting_point_ratio()

    prices = {col: [] for col in columns}
    prices["timestamp"] = []

    num = 0
    for linenum, row in enumerate(_read_csv(filename)):
        # Add price point if enough was skipped
        if linenum % point_ratio == 0:
            prices["timestamp"].append(
                datetime.fromisoformat(row["timestamp"]))

            for col in columns:
                # Add only non-zero values
                num = float(row[col])
                if num > 0:
                    prices[col].append(num)

    return prices


def get_csv_line_count(filename: str) -> int:
    """Count the number of lines in a csv file.

    Args:
        filename (str): Path to CSV file which line count to calculate.

    Returns:
        int: The number of lines in the file with the header being excluded.
    """
    lines = 0

    with open(filename, "rb") as infile:
        buf_size = 1024 * 1024
        read_infile = infile.raw.read

        buf = read_infile(buf_size)
        while buf:
            lines += buf.count(b"\n")
            buf = read_infile(buf_size)

    return lines - 1  # excluding the header from the number of lines


def load_bundles() -> Dict[str, List[str]]:
    """Load created bundles.

    Returns:
        Dict[str, List[str]]: Names and contents of created bundles.
    """
    with open(BUNDLES_FILEPATH, "r", encoding="utf-8") as file:
        return json.loads(file.read())


def load_bundle_ids() -> List[str]:
    """Read all the existing bundle ids.

    Returns:
        List[str]: The ids of existing bundles.
    """
    return list(load_bundles().keys())


def load_bundle(bundle_id: str) -> Dict[str, float]:
    """Load a specific bundle.

    Args:
        bundle_id (str): The id of bundle.

    Raises:
        ValueError: If bundle id was not found.

    Returns:
        Dict[str, float]: The contents of requested bundle.
    """
    bundles = load_bundles()

    if bundle_id not in bundles.keys():
        raise ValueError("GIVEN BUNDLE ID NOT FOUND")

    return bundles[bundle_id]


def valid_bundle_ids(bundle_ids: List[str]) -> bool:
    """Check whether requested bundle ids exist in the BUNDLES file.

    Args:
        bundle_ids (List[str]): Bundle ids to check.

    Returns:
        bool: True if exist, False otherwise.
    """
    ids = load_bundle_ids()

    for bundle_id in bundle_ids:
        if bundle_id not in ids:
            return False

    return True


def create_bundle(bundle_id: str) -> None:
    """Create a bundle of cryptocurrencies.

    Args:
        bundle_id (str): The id of bundle.

    Raises:
        ValueError: If bundle id already taken.
    """
    bundles = load_bundles()

    if bundle_id in bundles.keys():
        raise ValueError("BUNDLE NAME ALREADY TAKEN")

    bundles[bundle_id] = {}

    with open(BUNDLES_FILEPATH, "w", encoding="utf-8") as file:
        file.write(json.dumps(bundles, indent=4))


def add_cryptocur_to_bundle(
    bundle_id: str, cryptocur_id: str, amount: int
) -> None:
    """Add a cryptocurrency to a bundle.

    Args:
        bundle_id (str): The id of bundle to add cryptocurrency to.
        cryptocur_id (str): The id of cryptocurrency to add to bundle.
        amount (int): Amount of cryptocurrency to add.

    Raises:
        ValueError: If cryptocurrency id was not found, bundle id was
        not found or cryptocurrency already added to bundle.
    """
    if not valid_cryptocurrency_ids([cryptocur_id]):
        raise ValueError("GIVEN CRYPTOCURRENCY ID NOT FOUND")

    bundles = load_bundles()

    if bundle_id not in bundles.keys():
        raise ValueError("BUNDLE NOT FOUND")

    if cryptocur_id in bundles[bundle_id].values():
        raise ValueError("CRYPTOCURRENCY ALREADY IN BUNDLE")

    bundles[bundle_id][cryptocur_id] = amount

    with open(BUNDLES_FILEPATH, "w", encoding="utf-8") as file:
        file.write(json.dumps(bundles, indent=4))

    _update_bundle_prices(bundle_id, bundles[bundle_id])


def remove_cryptocur_from_bundle(bundle_id: str, cryptocur_id: str) -> None:
    """Remove a cryptocurrency from bundle.

    Args:
        bundle_id (str): The id of bundle to remove cryptocurrency from.
        cryptocur_id (str): The id of cryptocurrency to remove from bundle.

    Raises:
        ValueError: If bundle id was not found or cryptocurrency
        is not present in bundle.
    """
    bundles = load_bundles()

    if bundle_id not in bundles.keys():
        raise ValueError("BUNDLE NOT FOUND")

    if cryptocur_id not in bundles[bundle_id].keys():
        raise ValueError("CRYPTOCURRENCY NOT ADDED TO BUNDLE")

    bundles[bundle_id].pop(cryptocur_id)

    with open(BUNDLES_FILEPATH, "w", encoding="utf-8") as file:
        file.write(json.dumps(bundles, indent=4))

    _update_bundle_prices(bundle_id, bundles[bundle_id])


def _update_bundle_prices(
    bundle_id: str, cryptocurrencies: Dict[str, int]
) -> None:
    with open(TMP_FILEPATH, "w", encoding="utf-8", newline="") as csvoutput:
        header = ["timestamp"] + load_bundle_ids()

        writer = csv.DictWriter(csvoutput, fieldnames=header)
        writer.writeheader()

        for cur_price_row, bundle_price_prow in zip_longest(
            _read_csv(PRICES_FILEPATH), _read_csv(BUNDLE_PRICES_FILEPATH)
        ):
            if not bundle_price_prow:
                bundle_price_prow = {"timestamp": cur_price_row["timestamp"]}

            bundle_price_prow[bundle_id] = sum(
                [
                    float(cur_price_row[cryptocur_id]) * amount
                    for cryptocur_id, amount
                    in cryptocurrencies.items()
                ]
            )

            writer.writerow(bundle_price_prow)

    # Replacing BUNDLE_PRICES file with a created one
    os.remove(BUNDLE_PRICES_FILEPATH)
    os.rename(TMP_FILEPATH, BUNDLE_PRICES_FILEPATH)


def delete_bundle(bundle_id: str) -> None:
    """Delete an existing bundle of cryptocurrencies

    Args:
        bundle_id (str): The id of bundle to delete.

    Raises:
        ValueError: If bundle was not found.
    """
    bundles = load_bundles()

    if bundle_id not in bundles.keys():
        raise ValueError("GIVEN BUNDLE ID NOT FOUND")

    bundle = bundles.pop(bundle_id)

    with open(BUNDLES_FILEPATH, "w", encoding="utf-8") as file:
        file.write(json.dumps(bundles, indent=4))

    # Remove the column of the bundle if any cryptocurrencies were added.
    if bundle:
        _remove_column_from_csv(BUNDLE_PRICES_FILEPATH, bundle_id)


def exists_in_bundles(cryptocurrency_id: str) -> bool:
    """Check whether cryptocurrency is added to a bundle.

    Args:
        cryptocurrency_id (str): The id of cryptocurrency.

    Returns:
        bool: True if added to the bundle, False otherwise.
    """
    bundles = load_bundles()

    for cur_list in bundles.values():
        if cryptocurrency_id in cur_list:
            return True

    return False


def load_cryptocurrency_ids() -> List[str]:
    """Load the IDS file.

    Returns:
        List[str]: The id list of added cryptocurrencies.
    """
    with open(IDS_FILEPATH, "r", encoding="utf-8") as file:
        return json.loads(file.read())


def valid_cryptocurrency_ids(cryptocurrency_ids: List[str]) -> bool:
    """Check whether requested cryptocurrency ids exist in the IDS file.

    Args:
        cryptocurrency_ids (List[str]): Cryptocurrency ids to check.

    Returns:
        bool: True if exist, False otherwise.
    """
    ids = load_cryptocurrency_ids()

    for cur_id in cryptocurrency_ids:
        if cur_id not in ids:
            return False

    return True


def add_new_cryptocurrency(cryptocurrency_id: str) -> List[str]:
    """Add a new cryptocurrency to the data files.

    Args:
        cryptocurrency_id (str): The id of cryptocurrency.

    Raises:
        ValueError: If cryptocurrency was already added.

    Returns:
        List[str]: Updated list of added cryptocurrencies.
    """
    # Check if already exists
    ids = load_cryptocurrency_ids()
    if cryptocurrency_id in ids:
        raise ValueError("GIVEN CRYPTOCURRENCY ID ALREADY ADDED")

    _add_new_id(cryptocurrency_id)
    _add_column_to_csv(PRICES_FILEPATH, cryptocurrency_id)
    return ids + [cryptocurrency_id]


# Add a new ID to the IDS file
def _add_new_id(cryptocurrency_id: str) -> None:
    with open(IDS_FILEPATH, "r", encoding="utf-8") as name_input:
        ids = json.loads(name_input.read())

    ids.append(cryptocurrency_id)

    with open(IDS_FILEPATH, "w", encoding="utf-8") as name_output:
        name_output.write(json.dumps(ids, indent=4))


# Add new column to the PRICES file and set
# its value to 0 for all existing rows
def _add_column_to_csv(filename: str, column_name: str) -> None:
    with open(filename, "r", encoding="utf-8") as csvinput:
        with open(
            TMP_FILEPATH, "w", encoding="utf-8", newline=""
        ) as csvoutput:
            # Creating a reader and a new header list with the new
            # cryptocurrency id in the end
            reader = csv.DictReader(csvinput)
            header = reader.fieldnames + [column_name]

            writer = csv.DictWriter(csvoutput, fieldnames=header)
            writer.writeheader()

            for row in reader:
                row[column_name] = 0
                writer.writerow(row)

    # Replacing PRICES file with the updated one
    os.remove(filename)
    os.rename(TMP_FILEPATH, filename)


def remove_cryptocurrency(cryptocurrency_id: str) -> List[str]:
    """Remove an added cryptocurrency from the data files.

    Args:
        cryptocurrency_id (str): The id of cryptocurrency.

    Raises:
        ValueError: If cryptocurrency was not found or
        it still exists in a bundle.

    Returns:
        List[str]: Updated cryptocurrency ids without removed cryptocurrency.
    """
    # Check whether requested cryptocurrency exists in the id list.
    ids = load_cryptocurrency_ids()
    if cryptocurrency_id not in ids:
        raise ValueError("GIVEN CRYPTOCURRENCY ID NOT FOUND")

    if exists_in_bundles(cryptocurrency_id):
        raise ValueError(
            "REMOVE CRYPTOCURRENCY FROM BUNDLES BEFORE DELETING IT")

    _remove_id(cryptocurrency_id)
    _remove_column_from_csv(PRICES_FILEPATH, cryptocurrency_id)

    ids.remove(cryptocurrency_id)
    return ids


# Remove an ID from the NAMES file
def _remove_id(cryptocurrency_id: str) -> None:
    with open(IDS_FILEPATH, "r", encoding="utf-8") as name_input:
        ids = json.loads(name_input.read())

    ids.remove(cryptocurrency_id)

    with open(IDS_FILEPATH, "w", encoding="utf-8") as name_output:
        name_output.write(json.dumps(ids, indent=4))


# Remove a column from a csv file
def _remove_column_from_csv(filename: str, column_name: str) -> None:
    with open(filename, "r", encoding="utf-8") as csvinput:
        with open(
            TMP_FILEPATH, "w", encoding="utf-8", newline=""
        ) as csvoutput:
            # Creating a reader and a new header list without given ID
            reader = csv.DictReader(csvinput)
            header = list(reader.fieldnames)
            header.remove(column_name)

            writer = csv.DictWriter(csvoutput, fieldnames=header)
            writer.writeheader()

            for row in reader:
                row.pop(column_name)
                writer.writerow(row)

    # Replacing PRICES file with the updated one
    os.remove(filename)
    os.rename(TMP_FILEPATH, filename)


def write_cryptocur_prices_entry(
    data: Dict[str, Union[datetime, float]],
    header: Optional[List[str]] = None
) -> None:
    """Write a new entry to prices using given cryptocurrency price data.

    Args:
        data (Dict[str, Union[datetime, float]]): Cryptocurrency price data.
        header (Optional[List[str]], optional): Header of prices file.
        Defaults to None.

    Raises:
        ValueError: If given price data does not contain a price
        for any of added cryptocurrencies.
    """
    # Load cryptocurrency ids as the header if not given
    if not header:
        header = ["timestamp"] + load_cryptocurrency_ids()

    # Validating each cryptocurrency's value and
    # raising a ValueError if some wasn"t provided.
    for cryptocurrency in header[1:]:
        if cryptocurrency not in data.keys():
            raise ValueError("CRYPTOCURRENCY VALUE MISSING")

    _write_csv_entry(PRICES_FILEPATH, data, header)


def write_bundle_prices_entry(
    cryptocur_prices: Dict[str, Union[datetime, float]]
) -> None:
    """Update bundle prices using given cryptocurrency prices.

    Args:
        cryptocurrency_prices (Dict[str, Union[datetime, float]]): The prices
        of all added cryptocurrencies.
    """
    bundles = load_bundles()
    bundle_prices = {"timestamp": cryptocur_prices["timestamp"]}

    # Add a timestamp column in front of the cryptocurrency names
    header = ["timestamp"] + list(bundles.keys())

    # Calculating prices of each bundle using given cryptocurrency prices
    for bundle_id, cryptocurrencies in bundles.items():
        bundle_prices[bundle_id] = sum([
            float(cryptocur_prices[cryptocur_id]) * amount
            for cryptocur_id, amount
            in cryptocurrencies.items()
        ])

    _write_csv_entry(BUNDLE_PRICES_FILEPATH, bundle_prices, header)


def convert_prices(factor: float) -> None:
    """Convert stored cryptocurrency and bundle prices using given factor.

    Args:
        factor (float): The factor to multiply current prices by.
    """
    cryptocurr_header = ["timestamp"] + load_cryptocurrency_ids()
    _convert_price_file_values(PRICES_FILEPATH, cryptocurr_header, factor)

    bundle_header = ["timestamp"] + load_bundle_ids()
    _convert_price_file_values(BUNDLE_PRICES_FILEPATH, bundle_header, factor)


def _convert_price_file_values(
    filename: str, header: List[str], factor: float
) -> None:
    with open(TMP_FILEPATH, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)

        writer.writeheader()
        for row in _read_csv(filename):
            row = {
                key: (float(value) * factor if key != "timestamp" else value)
                for key, value in row.items()
            }

            writer.writerow(row)

    os.remove(filename)
    os.rename(TMP_FILEPATH, filename)


def _write_csv_entry(
    filename: str, data: Dict[str, Any], header: List[str]
) -> None:
    with open(filename, "a", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writerow(data)


def _write_csv_entries(
    filename: str, data: List[Dict[str, Any]], header: List[str]
) -> None:
    with open(filename, "a", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writerows(data)
