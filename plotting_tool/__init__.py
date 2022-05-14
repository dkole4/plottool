"""
A tool for tracking and plotting cryptocurrency prices.

Modules:

    background - Price updating module.
    commands   - User command handling modele.
    constants  - Constants used by the application.
    file       - File handling module.
    help       - User manual module.
    plot       - Price plotting module.
    request    - Data fetching module.
    settings   - User settings handling module.
    stats      - Data statistics handling module.
    util       - Utils module.
"""
from plotting_tool.commands import CommandHandler
from plotting_tool.file import ensure_data_files_existence


def main():
    """
    The main function of the program.
    """
    ensure_data_files_existence()
    command_handler = CommandHandler()
    command_handler.run()
