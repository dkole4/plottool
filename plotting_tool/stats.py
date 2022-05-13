"""
This module provides statistics-related functionality for the application.

Functions:

    statistics_to_str(Dict[str, Dict[str, float]]) -> str
"""
from typing import Dict


def statistics_to_str(stats: Dict[str, Dict[str, float]]) -> str:
    """Convert given cryptocurrency statictics into a string.

    Args:
        stats (Dict[str, Dict[str, float]]): Prices statistics
        of cryptocurrencies.

    Returns:
        str: String representation of given statistics.
    """
    stats_str = "\n"

    for currency, cur_stats in stats.items():
        stats_str += (
            f"\t- {currency:<15} [ min: {cur_stats['min']:<12.8g} | max:"
            f" {cur_stats['max']:<12.8g} | mean: {cur_stats['mean']:<12.8g}]\n"
        )

    return stats_str
