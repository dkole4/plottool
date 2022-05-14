"""
This module provides a command documentation for the user.

Functions:

    get_help_message(str) -> str
"""

HELP_DOCUMENTATION = (
    """
    - help        | Show this message.
    - help basic  | Show basic commands.
    - help cur    | Show cryptocurrency-related commands.
    - help bund   | Show bundle-related commands.
    """
)

BASIC_COMMAND_DOCUMENTATION = (
    """
    - quit                  | Exit the program.
    - print (message)       | Print a message.
    - eval (expression)     | Evaluate an arithmetic expression.
    - timetog               | Toggle time display.
    - settings              | Show user settings.
    - set (setting) (value) | Set setting value.
    - vscurrency (cur_code) | Change fiat currency.
    """
)

CUR_COMMAND_DOCUMENTATION = (
    """
    - curadd (cryptocur_id)            | Add a cryptocurrency.
    - curdel (cryptocur_id)            | Delete an added cryptocurrency.
    - curlist                          | Print all the added cryptocurrencies.
    - curplot (subplots) cur1 cur2 ... | Plot cryptocurrency prices.
    """
)

UPD_COMMAND_DOCUMENTATION = (
    """
    - updstart (update_time)   | Start the background updater.
    - updstop                  | Stop the background updater.
    - updstatus                | Show information about the updater.
    """
)

BUNDLE_COMMAND_DOCUMENTATION = (
    """
    - bundcreate (bundle_id)                      | Create a new bundle.
    - bunddel (bundle_id)                         | Delete a bundle.
    - bundlist                                    | Show the list of created bundles.
    - bundplot (subplots) bund1 bund2 ...         | Plot bundle prices.
    - bundadd (bundle_id) (cryptocur_id) (amount) | Add a cryptocurrency to a bundle.
    - bundrem (bundle_id) (cryptocur_id)          | Remove a cryptocurrency from a bundle.
    """
)

HELP_SECTIONS = {
    "": HELP_DOCUMENTATION,
    "basic": BASIC_COMMAND_DOCUMENTATION,
    "cur": CUR_COMMAND_DOCUMENTATION,
    "upd": UPD_COMMAND_DOCUMENTATION,
    "bund": BUNDLE_COMMAND_DOCUMENTATION
}


def get_help_message(section: str) -> str:
    """Get a user manual message.

    Args:
        section (str): Section of user manual to return.

    Raises:
        ValueError: If user manual section was not found.

    Returns:
        str: Section of user manual.
    """
    message = HELP_SECTIONS.get(section, None)
    if not message:
        raise ValueError("HELP SECTION NOT FOUND")

    return message
