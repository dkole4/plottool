"""
This module provides a user command handler for the application.

Classes:

    CommandHandler
"""
import time
from typing import Any, Callable, Dict, List, Optional

from plotting_tool import file
from plotting_tool import request
from plotting_tool import plot
from plotting_tool import stats
from plotting_tool import util
from plotting_tool.background import BackgroundUpdateThread
from plotting_tool.constants import COMMAND_LIST, PROGRAM_STATUS, SETTING
from plotting_tool.help import get_help_message
from plotting_tool.settings import SettingHandler
from plotting_tool.util import (
    greater_or_equal, parse_command_arguments, validate_command_arguments
)


class CommandHandler():
    """
    User command handler.
    """
    def __init__(self):
        """
        Command handler Constructor to initialize the object.
        """
        self._background_updater: BackgroundUpdateThread = None
        self.program_status: PROGRAM_STATUS = PROGRAM_STATUS.RUNNING

        setting_handler: SettingHandler = SettingHandler()
        self._use_time: bool = setting_handler.read_field(
            SETTING.USE_TIME)

        self._commands: Dict[COMMAND_LIST, Callable] = {
            COMMAND_LIST.QUIT: self.exit_program,
            COMMAND_LIST.HELP: self._show_help,
            COMMAND_LIST.PRINT: self._print_user_input,
            COMMAND_LIST.START_UPDATER: self._start_background_updater,
            COMMAND_LIST.CHECK_UPDATER_STATUS: self._check_updater_status,
            COMMAND_LIST.STOP_UPDATER:
                lambda: (self._stop_background_updater(command_call=True)),
            COMMAND_LIST.ADD_CURRENCY: self._add_currency,
            COMMAND_LIST.REMOVE_CURRENCY: self._remove_currency,
            COMMAND_LIST.LIST_CURRENCIES: self._list_currencies,
            COMMAND_LIST.PLOT_CURRENCIES: self._plot_currencies,
            COMMAND_LIST.CREATE_BUNDLE: self._create_bundle,
            COMMAND_LIST.DELETE_BUNDLE: self._delete_bundle,
            COMMAND_LIST.ADD_TO_BUNDLE: self._add_to_bundle,
            COMMAND_LIST.REMOVE_FROM_BUNDLE: self._remove_from_bundle,
            COMMAND_LIST.LIST_BUNDLES: self._list_bundles,
            COMMAND_LIST.PLOT_BUNDLES: self._plot_bundles,
            COMMAND_LIST.TOGGLE_TIME: self._toggle_time,
            COMMAND_LIST.SHOW_SETTINGS: self._show_settings,
            COMMAND_LIST.CHANGE_SETTINGS: self._change_settings,
            COMMAND_LIST.CHANGE_VS_CURRENCY: self._change_vs_currency,
            COMMAND_LIST.EVAL: self._eval_user_input
        }

    def run(self) -> None:
        """
        Start the handler.
        """
        self._print(">>>>> STARTING THE PROGRAM")

        while self.program_status == PROGRAM_STATUS.RUNNING:
            self._process_next_command()

    def exit_program(self) -> None:
        """
        Stop processing user commands and exit the program.
        """
        # Terminate the Background Update Thread if it was started
        if self._background_updater is not None:
            self._stop_background_updater()
            self._background_updater = None

        self._print(">>>>> TERMINATING THE PROGRAM")
        self.program_status = PROGRAM_STATUS.TERMINATED

    # Get input from the user
    def _get_user_input(self) -> str:
        self._print("----- Enter command:")
        return input("> ")

    # Show a user manual message.
    def _show_help(self, section: str = "") -> None:
        self._print(get_help_message(section))

    # Print message to the user
    def _print(self, message: str) -> None:
        if self._use_time:
            print(f"[{time.strftime('%X')}] {message}")
        else:
            print(message)

    # Print caught error to the user
    def _print_error(self, error: Exception) -> None:
        if isinstance(error, KeyError):
            self._print("!!! ENTERED COMMAND NOT FOUND")
        elif isinstance(error, Exception):
            self._print(f"!!! {str(error).upper()}")
        else:
            self._print("!!! UNEXPECTED PROGRAM BEHAVIOUR, " +
                        f"RECEIVED ERROR: {error}")

    # Ask the user for a new command and process it
    def _process_next_command(self) -> None:
        user_command = self._get_user_input()
        self._process_command(user_command)

    # Process current command
    def _process_command(self, user_input: str) -> None:
        # Split the command and argument list into separate variables
        command = COMMAND_LIST.EMPTY
        args = None

        if user_input != COMMAND_LIST.EMPTY:
            (command, *args) = user_input.split()

        try:
            self._commands[command](*args)
        except Exception as e:
            self._print_error(e)

    # Switch time showing setting.
    def _toggle_time(self):
        self._use_time = not self._use_time
        setting_handler = SettingHandler()
        setting_handler.set_field(SETTING.USE_TIME, self._use_time)

    # Show current user settings.
    def _show_settings(self):
        setting_handler = SettingHandler()
        self._print(setting_handler.get_setting_repr())

    # Change user setting value to a new one.
    def _change_settings(self, setting_name: str, new_value: Any) -> None:
        setting = SETTING(setting_name)
        setting_handler = SettingHandler()
        setting_handler.set_field(setting, new_value)
        self._print(f">>>>> SETTING {setting_name} WAS SET TO {new_value}")

    # Evaluate expession given by user and print the result.
    # Meant to be used ONLY for arithmetic expressions.
    def _eval_user_input(self, *user_input: List[str]) -> None:
        output = eval(" ".join(user_input))
        self._print(f">>>>> OUTPUT: {output}")

    # Change program vs currency and convert stored prices using
    # factor of new currency compared to the previous one.
    @parse_command_arguments(str, float)
    @validate_command_arguments(None, greater_or_equal(0))
    def _change_vs_currency(
        self, currency_code: str, convert_factor: float
    ) -> None:
        if not request.check_vs_currency_existence(currency_code):
            raise ValueError("GIVEN CURRENCY WAS NOT FOUND")

        # Pause the updater while updating settings
        # and converting existing prices.
        self._pause_background_updater()
        setting_handler = SettingHandler()
        setting_handler.set_field(SETTING.VS_CURRENCY, currency_code)
        file.convert_prices(convert_factor)

        # Update background updater currency if one is running.
        if self._background_updater:
            self._background_updater.set_vs_currency(currency_code)

        self._resume_background_updater()
        self._print(f">>>>> VS CURRENCY WAS UPDATED TO {currency_code}")

    # Start Background Updater.
    @util.parse_command_arguments(int)
    @util.validate_command_arguments(greater_or_equal(60))
    def _start_background_updater(
        self, pause_time: Optional[int] = 60
    ) -> None:
        if self._background_updater and not self._background_updater.stopped():
            raise ValueError("REQUESTED TASK IS ALREADY STARTED")

        setting_handler = SettingHandler()
        vs_currency = setting_handler.read_field(SETTING.VS_CURRENCY)
        self._background_updater = BackgroundUpdateThread(
            pause_time, vs_currency
        )
        self._background_updater.start()
        self._print(">>>>> STARTING THE BACKGROUND PRICE UPDATER")

    def _pause_background_updater(self) -> None:
        if self._background_updater:
            self._background_updater.pause()

    def _resume_background_updater(self) -> None:
        if self._background_updater:
            self._background_updater.resume()

    # Stop the Background Update Thread
    def _stop_background_updater(self, command_call: bool = False) -> None:
        if self._background_updater and not self._background_updater.stopped():
            self._print(">>>>> STOPPING THE BACKGROUND PRICE UPDATER")
            self._background_updater.stop()
        elif command_call:
            raise ValueError("REQUESTED TASK NOT FOUND OR STARTED")

    # Update cryptocurrency ids inside the Updater
    def _update_background_updater(self, new_ids: List[str]) -> None:
        if self._background_updater:
            self._background_updater.set_cryptocur_ids(new_ids)

    # Check the status of the Updater
    def _check_updater_status(self) -> None:
        if self._background_updater:
            print(str(self._background_updater))
        else:
            raise ValueError("REQUESTED TASK NOT FOUND OR STARTED")

    # Add a new cryptocurrency to the list of tracked cryptocurrencies
    @util.parse_command_arguments(str)
    def _add_currency(self, cryptocurrency_id: str) -> None:
        if not request.check_cryptocurrency_existence(cryptocurrency_id):
            raise ValueError("REQUESTED CRYPTOCURRENCY NOT FOUND")

        self._pause_background_updater()
        output = file.add_new_cryptocurrency(cryptocurrency_id)

        self._update_background_updater(output)
        self._print(f">>>>> NEW CRYPTOCURRENCY {cryptocurrency_id}" +
                    " WAS ADDED TO THE LIST")

        self._resume_background_updater()

    # Remove an existing cryptocurrency from
    # the list of tracked cryptocurrencies
    @util.parse_command_arguments(str)
    def _remove_currency(self, cryptocurrency_id: str) -> None:
        self._pause_background_updater()
        output = file.remove_cryptocurrency(cryptocurrency_id)

        self._update_background_updater(output)
        self._print(f">>>>> CRYPTOCURRENCY {cryptocurrency_id}" +
                    " WAS REMOVED FROM THE LIST")

        self._resume_background_updater()

    # List all the existing cryptocurrencies.
    def _list_currencies(self):
        stats_str = stats.statistics_to_str(file.load_cryptocur_statistics())
        self._print(stats_str)

    # Plot cryptocurrencies to a graph
    def _plot_currencies(self, *args: List[str]) -> None:
        (subplots, *cryptocurrency_ids) = args
        subplots = int(subplots)

        self._pause_background_updater()
        prices_data = file.load_cryptocur_plot_prices(cryptocurrency_ids)
        self._resume_background_updater()

        plot.validate_currency_arguments(
            cryptocurrency_ids, subplots, prices_data)
        plot.plot_prices(prices_data, cryptocurrency_ids, subplots)

    # Create a bundle of cryptocurrencies
    def _create_bundle(self, bundle_id: str) -> None:
        file.create_bundle(bundle_id)
        self._print(">>>>> BUNDLE WAS SUCCESSFULLY CREATED")

    # Add a cryptocurrency to bundle
    @parse_command_arguments(str, str, float)
    @validate_command_arguments(None, None, greater_or_equal(0))
    def _add_to_bundle(
        self, bundle_id: str, cryptocur_id: str, amount: float
    ) -> None:
        self._pause_background_updater()
        file.add_cryptocur_to_bundle(bundle_id, cryptocur_id, amount)
        self._resume_background_updater()

        self._print(">>>>> BUNDLE WAS SUCCESSFULLY UPDATED")

    # Remove a cryptocurrency from bundle
    def _remove_from_bundle(self, bundle_id: str, cryptocur_id: str) -> None:
        self._pause_background_updater()
        file.remove_cryptocur_from_bundle(bundle_id, cryptocur_id)
        self._resume_background_updater()

        self._print(">>>>> BUNDLE WAS SUCCESSFULLY UPDATED")

    # Delete an existing bundle of cryptocurrencies
    def _delete_bundle(self, bundle_id: str) -> None:
        file.delete_bundle(bundle_id)
        self._print(">>>>> BUNDLE WAS SUCCESSFULLY DELETED")

    # Plot bundle prices.
    def _plot_bundles(self, *args: List[str]) -> None:
        (subplots, *bundle_ids) = args
        subplots = int(subplots)

        self._pause_background_updater()
        prices_data = file.load_bundle_plot_prices(bundle_ids)
        self._resume_background_updater()

        plot.validate_bundle_arguments(bundle_ids, subplots, prices_data)
        plot.plot_prices(prices_data, bundle_ids, subplots)

    # List all the created cryptocurrency bundles
    def _list_bundles(self) -> None:
        bundles = file.load_bundles()

        repr_string = "\n"
        for bund_id, bundle in bundles.items():
            repr_string += f"\t {bund_id}:\n"
            repr_string += "\t\t[ {} ]\n".format(
                ", ".join([
                    f"{cur_id}: {amount}"
                    for cur_id, amount
                    in bundle.items()
                ])
            )

        self._print(repr_string)

    # Test command, print entered input
    def _print_user_input(self, *arguments: List[str]) -> None:
        argument_string = " ".join(arguments)
        self._print(f"----- YOUR INPUT:\n{argument_string}")
