"""
This module provides a Setting Handler for the application.

Classes:

    SettingHandler
"""
import json
import os
from typing import Any

from plotting_tool.constants import (
    DIRECTLY_MUTABLE_SETTINGS, SETTING_SET_CHECKS, SETTINGS_PATH,
    SETTINGS_DEFAULT_STATE, SETTING_TYPE, SETTING
)


class SettingHandler():
    """
    User settings handler of the program.
    """
    def __init__(self) -> None:
        self._load_settings()

    def read_field(self, field_name: SETTING) -> Any:
        """Read the value of a field of user settings.

        Args:
            field_name (SETTING): The name of the field.

        Raises:
            KeyError: If setting field was not found.

        Returns:
            Any: The value of the field.
        """
        return self.settings[field_name.value]

    def set_field(
        self, setting: SETTING, value: Any, command_call: bool = False
    ) -> None:
        """Set the value of a field of user settings to given value.

        Args:
            field_name (SETTING): The name of field which
                value needs to be changed.
            value (Any): The new value of the field.
            command_call (bool): Whether the setting change is
            done directly by "set" user command. Defaults to False.

        Raises:
            KeyError: If setting field was not found or
            value type or value is invalid.
        """
        if command_call and setting not in DIRECTLY_MUTABLE_SETTINGS:
            raise ValueError("SETTING CAN NOT BE CHANGED DIRECTLY")

        try:
            value = SETTING_TYPE[setting](value)
        except ValueError as e:
            raise ValueError("INVALID SETTING VALUE TYPE") from e

        if (
            setting in SETTING_SET_CHECKS.keys() and
            not SETTING_SET_CHECKS[setting](value)
        ):
            raise ValueError("INVALID SETTING VALUE")

        self.settings[setting.value] = value
        self._update_settings()

    def get_setting_repr(self) -> str:
        """Get string representation of current settings.

        Returns:
            str: String representation of current settings.
        """
        repr_string = "\n"
        for setting_name, value in self.settings.items():
            repr_string += f"\t[ {setting_name:_>25}: {value:>10} ]\n"
        return repr_string

    def _update_settings(self) -> None:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.settings, indent=4))

    def _load_settings(self) -> None:
        # Initialize settings if setting file not found,
        # use existing one otherwise.
        if not os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
                file.write(json.dumps(SETTINGS_DEFAULT_STATE, indent=4))
            self.settings = SETTINGS_DEFAULT_STATE
        else:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
                self.settings = json.load(file)
