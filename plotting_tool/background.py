"""
This module provides a background updater class for fetching
cryptocurrency prices and saving them to CSV files.

Classes:

    BackgroundUpdateThread
"""
from datetime import datetime
import threading
from typing import List

from plotting_tool import request
from plotting_tool import file
from plotting_tool.constants import (
    DEFAULT_THREAD_UPDATE_TIME, MAX_UPDATE_RETRIES, THREAD_STATUS
)


class BackgroundUpdateThread(threading.Thread):
    """
    Thread for updating cryptocurrency and bundle prices in background.
    """
    def __init__(
        self,
        update_time: int = DEFAULT_THREAD_UPDATE_TIME,
        vs_currency: str = "usd"
    ) -> None:
        """Background Update Thread Constructor to initialize the object.

        Args:
            update_time (int, optional): Pause between updates in seconds.
            Defaults to DEFAULT_THREAD_UPDATE_TIME.
            vs_currency (str, optional): Fiat currency to use in price
            fetching. Defaults to "usd".
        """
        threading.Thread.__init__(self)
        self._error_count: int = 0
        self._update_time: int = update_time
        self._vs_currency: str = vs_currency
        self._last_update: str = "WAITING UPDATE"
        self._stop: threading.Event = threading.Event()

        self._currency_ids: List[str] = file.load_cryptocurrency_ids()
        if not self._currency_ids:
            raise ValueError("CANT START UPDATER, NO CRYPTOCURRENCY FOUND")

        self.status: THREAD_STATUS = THREAD_STATUS.RUNNING

    def __repr__(self) -> str:
        representation = ("  +-------------------------------+\n"
                          "  |  BACKGROUND  UPDATE  THREAD   |\n"
                          "  +-------------------------------+\n"
                          "  | > STATUS:      {:<14} |\n"
                          "  | > LAST UPDATE: {:<14} |\n"
                          "  | > UPDATE TIME: {:<14} |\n"
                          "  +-------------------------------+")
        return representation.format(
            self.status.name, self._last_update, f"{self._update_time} s")

    def set_cryptocur_ids(self, new_ids: List[str]) -> None:
        """Update cryptocurrency ids stored in the thread.

        Args:
            new_ids (List[str]): New cryptocurrency ids.
        """
        self._currency_ids = new_ids

    def set_vs_currency(self, new_vs_currency: str) -> None:
        """Update vs currency stored in the thread.

        Args:
            new_vs_currency (str): The code of new vs currency to
            use in price tracking.
        """
        self._vs_currency = new_vs_currency

    def pause(self) -> None:
        """
        Pause the thread and prevent it from updating the prices.
        """
        if self.status == THREAD_STATUS.RUNNING:
            self.status = THREAD_STATUS.PAUSED

    def resume(self) -> None:
        """
        Resume the thread if it was paused.
        """
        if self.status == THREAD_STATUS.PAUSED:
            self.status = THREAD_STATUS.RUNNING

    def run(self) -> None:
        while not self.stopped():
            self._stop.wait(self._update_time)

            if self.status == THREAD_STATUS.RUNNING:
                # Update prices if the thread isn't paused or stopped.
                self._update_prices()

    def stop(self) -> None:
        """
        Stop the thread.
        """
        self.status = THREAD_STATUS.STOPPED
        self._stop.set()

    def stopped(self) -> bool:
        """Is thread stopped.

        Returns:
            bool: True if stopped, False otherwise.
        """
        return self._stop.isSet()

    def _update_prices(self) -> None:
        # FORMAT: { coin_name: { vs_currency: value }, ... }
        result = request.fetch_data(self._currency_ids, self._vs_currency)

        # Add to the error count if update has failed.
        if not result:
            self._increase_error_count()
            return

        # Transform entries into coin_name:value instead of
        # coin_name: { vs_currency: value }
        for key, value in result.items():
            result[key] = value[self._vs_currency]

        # Adding the timestamp to the prices
        result["timestamp"] = datetime.now()

        # Updating currency and bundle prices using fetched data
        file.write_cryptocur_prices_entry(
            result, ["timestamp"] + self._currency_ids)
        file.write_bundle_prices_entry(result)

        self._last_update = result["timestamp"].strftime("%X")

    # Keep track of failed attempts of updating prices and
    # stop the thread if too many attempts have failed.
    def _increase_error_count(self) -> None:
        self._error_count += 1
        if self._error_count > MAX_UPDATE_RETRIES:
            self.stop()
