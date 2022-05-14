"""
This module provides plotting functionality of the application.

Functions:

    plot_prices(Dict[str, List[Union[datetime, float]]], List[str], int)

    validate_currency_arguments(
        List[str], int, Dict[str, List[Union[datetime, float]]])

    validate_bundle_arguments(
        List[str], int, Dict[str, List[Union[datetime, float]]])

    valid_plot_arguments(int, int, Dict[str, List[Union[datetime, float]]])
    -> bool:

    check_price_range(int, int) -> int

    plot_values(Axes, List[datetime], List[float], str, str)

    enable_grid(Axes)

    adjust_limits(Axes, Axes, List[float], List[float])

    use_annotations(Axes, List[datetime], List[float], str)
"""
from datetime import datetime
from statistics import mean
from typing import Dict, List, Union

from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from plotting_tool import file
from plotting_tool.constants import SETTING
from plotting_tool.settings import SettingHandler


# Plot given cryptocurrencies/bundles using timestamps and
# values of cryptocurrencies/bundles at that points of time.
def plot_prices(
    data: Dict[str, List[Union[datetime, float]]],
    axis_names: List[str],
    subplots: int = 1
) -> None:
    """Plot prices of cryptocurrencies or bundles.

    Args:
        data (Dict[str, List[Union[datetime, float]]]): Prices of
        cryptocurrencies/bundles.
        axis_names (List[str]): Names of cryptocurrencies/bundles
        being plotted.
        subplots (int, optional): Number of plots to use. Defaults to 1.
    """
    plt.style.use(["dark_background"])

    if subplots > 1:
        fig, axes = plt.subplots(subplots, 1, sharex=True)
    else:
        axes = [plt.subplot()]
    axes[-1].set_xlabel("timestamp")

    for i, cur_ax_name in enumerate(axis_names):
        # Use only the last prices_len timestamps in plotting and adjusting
        prices_len = len(data[cur_ax_name])
        timestamps = data["timestamp"][-prices_len:]

        if i >= subplots:
            cloned_ax = axes[i % subplots].twinx()
            plot_values(cloned_ax, timestamps,
                        data[cur_ax_name], cur_ax_name, "orange")
            adjust_limits(axes[i % subplots], cloned_ax,
                          data[axis_names[i % subplots]],
                          data[cur_ax_name])
        else:
            plot_values(axes[i], timestamps, data[cur_ax_name],
                        cur_ax_name)
            # Enable grid if current cryptocurrency/bundle will
            # not be accompanied by another cryptocurrency/bundle
            if len(axis_names) == subplots or (i+1) * 2 > len(axis_names):
                enable_grid(axes[i])

    plt.tight_layout()
    plt.show()


def validate_currency_arguments(
    cryptocurrency_ids: List[str],
    subplots: int,
    prices: Dict[str, List[Union[datetime, float]]]
) -> None:
    """Check whether arguments are valid to be used in plot_prices function.

    Args:
        cryptocurrency_ids (List[str]): Ids of cryptocurrencies
        which prices to plot.
        subplots (int): Number of subplots to use in plotting.
        prices (Dict[str, List[Union[datetime, float]]]): Cryptocurrency
        prices to plot.

    Raises:
        ValueError: If given cryptocurrencies are not found, numbers
        of cryptocurrencies and subplots are not suitable for plotting
        or price data is missing for one of given cryptocurrencies.
    """
    if not valid_plot_arguments(len(cryptocurrency_ids), subplots, prices):
        raise ValueError(
            "INVALID SUBPLOT NUMBER, INVALID NUMBER OF CRYPTOCURRENCIES OR "
            "ONE OF GIVEN CURRENCIES DOES NOT HAVE ANY SAVED PRICE VALUES"
        )

    if not file.valid_cryptocurrency_ids(cryptocurrency_ids):
        raise ValueError("GIVEN CRYPTOCURRENCY IDS NOT FOUND")


def validate_bundle_arguments(
    bundle_ids: List[str],
    subplots: int,
    prices: Dict[str, List[Union[datetime, float]]]
) -> None:
    """Check whether arguments are valid to be used in plot_prices function.

    Args:
        bundle_ids (List[str]): Ids of bundles which prices to plot.
        subplots (int): Number of subplots to use in plotting.
        prices (Dict[str, List[Union[datetime, float]]]): Bundle
        prices to plot.

    Raises:
        ValueError: If given bundles are not found, numbers of
        cryptocurrencies and subplots are not suitable for plotting
        or price data is missing for one of given bundles.
    """
    if not valid_plot_arguments(len(bundle_ids), subplots, prices):
        raise ValueError(
            "INVALID SUBPLOT NUMBER, INVALID NUMBER OF BUNDLES OR "
            "ONE OF GIVEN BUNDLE DOES NOT HAVE ANY SAVED PRICE VALUES"
        )

    if not file.valid_bundle_ids(bundle_ids):
        raise ValueError("GIVEN BUNDLE IDS NOT FOUND")


def valid_plot_arguments(
    ax_num: int, subplots: int, prices: Dict[str, List[Union[datetime, float]]]
) -> bool:
    """Check whether arguments given to plot function are valid.

    Args:
        ax_num (int): number of axes
        subplots (int): number of subplots
        prices (Dict[str, List[Union[datetime, float]]]): prices to plot

    Returns:
        bool: True if arguments are valid, False otherwise.
    """
    for values in prices.values():
        if not values:
            return False

    return 0 < ax_num <= 8 and 0 < subplots <= 4 and \
        ax_num / subplots <= 2 and subplots <= ax_num


def check_price_range(mean_first: int, mean_second: int) -> int:
    """Check whether two cryptocurrencies/bundles are in the same y-axis range

    Args:
        mean_first (int): mean of the first cryptocurrency/bundle prices
        mean_second (int): mean of the second cryptocurrency/bundle prices

    Returns:
        int: -1 if the prices are within limits and the first prices are
            smaller, 1 if the prices are within limits and the first prices
            are larger, 0 otherwise.
    """
    if mean_first > mean_second:
        coeff = mean_first / mean_second
    else:
        coeff = mean_second / mean_first

    setting_handler = SettingHandler()
    same_limits_threshold = setting_handler.read_field(
        SETTING.SAME_LIMITS_THRESHOLD)

    if 1 + same_limits_threshold >= coeff:
        return 1

    return 0


def plot_values(
    axis: Axes, x: List[datetime], y: List[float],
    label: str, color: str = "white"
) -> None:
    """Plot values using an axis.

    Args:
        axis (Axes): Axis to use in plotting.
        x (List[datetime]): Values to use for the X-axis.
        y (List[float]): Values to use for the Y-axis.
        label (str): Label of the axis.
        color (str, optional): Color of the graph line. Defaults to "white".
    """
    # Using only the last y_len datetime objects in plotting if
    # cryptocurrency/bundle wasn't tracked all the time.
    axis.plot(x, y, color=color)
    axis.set_ylabel(label, color=color)

    use_annotations(axis, x, y)


def enable_grid(axis: Axes) -> None:
    """Enable grid for given axis.

    Args:
        axis (Axes): Axes to enable grid on.
    """
    axis.grid(True, which="major", color="w", alpha=0.25, linestyle="-")


def adjust_limits(
    axis1: Axes, axis2: Axes, prices1: List[float], prices2: List[float]
) -> None:
    """Adjust limits of two axes if their prices are in the same range

    Args:
        axis1 (Axes): First axis.
        axis2 (Axes): Second axis.
        prices1 (List[float]): Prices attached to first axis.
        prices2 (List[float]): Prices attached to second axis.
    """
    mean1, mean2 = mean(prices1), mean(prices2)
    coeff = check_price_range(mean1, mean2)

    if not coeff:
        return

    y_min, y_max = min(prices1 + prices2), max(prices1 + prices2)
    overall_mean = (mean1 + mean2) / 2

    # Adding offset to limits
    y_min -= overall_mean / 10
    y_max += overall_mean / 10

    axis1.set_ylim(y_min, y_max)
    axis2.set_ylim(y_min, y_max)

    # Enable grid, because both axis have the same limits.
    enable_grid(axis1)


def use_annotations(
    axis: Axes, x: List[datetime], y: List[float], color: str = "white"
) -> None:
    """Annotate price points of lines.

    Args:
        axis (Axes): Axis to annotate.
        x (List[datetime]): Values of x-axis.
        y (List[float]): Values of y-axis.
        color (str, optional): Color of annotation text. Defaults to "white".
    """
    # Use 1/10 of time between the first and last timepoints
    # and 1/10 of the average value of the cryprocurrency/bundle
    # as the units for spacing between annotations
    time_unit = (x[-1] - x[0]) / 10
    value_unit = mean(y) / 10

    last_point = None               # The last annotated datetime
    last_value = None               # The last annotated value
    shadow_offset = mean(y) / 1000  # Offset used for annotation's shadow
    max_value_len = 6               # Max char length of annotation

    for point, value in zip(x, y):
        # Draw an annotation if more or equal time is between than set
        # time unit or if current point is the first one.
        if not last_point or point - last_point >= time_unit or \
                abs(value - last_value) > value_unit:
            # Draw a shadow for the annotated text first for better visibility.
            axis.annotate(
                str(value)[:max_value_len],
                (point, value - shadow_offset),
                textcoords='data', fontweight='bold', color='black')

            axis.annotate(
                str(value)[:max_value_len],
                (point, value),
                textcoords='data', fontweight='bold', color=color)

            last_point = point
            last_value = value
