"""
This module stores constants needed for proper functioning of the application.

Classes:

    COMMAND_LIST
    PROGRAM_STATUS
    THREAD_STATUS
    SETTING
"""
from enum import Enum
import os


# commands.py

class COMMAND_LIST:
    """
    List of available user commands
    """
    EMPTY = ""
    QUIT = "quit"
    PRINT = "print"
    TOGGLE_TIME = "timetog"

    ADD_CURRENCY = "curadd"
    REMOVE_CURRENCY = "curdel"
    PLOT_CURRENCIES = "curplot"
    LIST_CURRENCIES = "curlist"

    START_UPDATER = "updstart"
    STOP_UPDATER = "updstop"
    CHECK_UPDATER_STATUS = "updstatus"

    CREATE_BUNDLE = "bundcreate"
    DELETE_BUNDLE = "bunddel"
    PLOT_BUNDLES = "bundplot"
    LIST_BUNDLES = "bundlist"
    ADD_TO_BUNDLE = "bundadd"
    REMOVE_FROM_BUNDLE = "bundrem"

    SHOW_SETTINGS = "settings"
    CHANGE_SETTINGS = "set"
    CHANGE_VS_CURRENCY = "vscurrency"

    EVAL = "eval"


class PROGRAM_STATUS:
    """
    Status of program.
    """
    TERMINATED = 0
    RUNNING = 1
    CAUGHT_ERROR = 2


# -----------
# requests.py

PRICES_URL = (
    "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}"
)


# -------------
# background.py

DEFAULT_THREAD_UPDATE_TIME = 60
MAX_UPDATE_RETRIES = 3


class THREAD_STATUS(Enum):
    """
    Status of background updater.
    """
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "LOCKED"


# -------
# file.py

# Application data folder.
DATA_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "data"
)

# Cryptocurrency prices file.
PRICES_FILEPATH = os.path.join(DATA_FOLDER, "prices.csv")
PRICES_DEFAULT_STATE = "timestamp\n"

# Bundles of cryptocurrencies created by user.
BUNDLES_FILEPATH = os.path.join(DATA_FOLDER, "bundles.json")
BUNDLES_DEFAULT_STATE = "{}"

# Prices of user bundles.
BUNDLE_PRICES_FILEPATH = os.path.join(DATA_FOLDER, "bundle_prices.csv")
BUNDLE_PRICES_DEFAULT_STATE = "timestamp\n"

# Names of cryptocurrencies used in the bundles.
IDS_FILEPATH = os.path.join(DATA_FOLDER, "ids.json")
IDS_DEFAULT_STATE = "[]"

# File to use in rewriting price files.
TMP_FILEPATH = os.path.join(DATA_FOLDER, "tmp.csv")


# -----------
# settings.py

class SETTING(Enum):
    """
    Settings of the program.
    """
    # Whether to show current time in the program.
    USE_TIME = "use_time"

    # Fiat currency to use in fetching cryptocurrency prices.
    VS_CURRENCY = "vs_currency"

    # Threshold that prices of two different cryptocurrencies need to
    # be within each other in order to be plotted in the same y-axis limits.
    # Threshold indicates the percentage difference in mean of prices.
    SAME_LIMITS_THRESHOLD = "same_limits_threshold"


SETTINGS_PATH = os.path.join(DATA_FOLDER, "settings.json")
SETTINGS_DEFAULT_STATE = {
    SETTING.USE_TIME.value: True,
    SETTING.VS_CURRENCY.value: "usd",
    SETTING.SAME_LIMITS_THRESHOLD.value: 1.5
}

DIRECTLY_MUTABLE_SETTINGS = [
    SETTING.SAME_LIMITS_THRESHOLD
]

SETTING_TYPE = {
    SETTING.USE_TIME: bool,
    SETTING.VS_CURRENCY: str,
    SETTING.SAME_LIMITS_THRESHOLD: float
}

SETTING_SET_CHECKS = {
    SETTING.SAME_LIMITS_THRESHOLD: lambda v: v > 0
}


# -------
# plot.py

# Default threshold to use in comparing mean prices of currencies in plotting.
SAME_LIMITS_THRESHOLD = 1.5
