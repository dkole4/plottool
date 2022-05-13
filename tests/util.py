import os


TEST_DATA_FOLDER = os.path.join(
    os.path.dirname(__file__),
    ".testdata"
)


def get_filepath(filename: str) -> str:
    """Get the path to a test data file.

    Args:
        filename (str): Name of the test data file.

    Returns:
        str: Path to the test data file.
    """
    return os.path.join(
        TEST_DATA_FOLDER,
        filename
    )


SETTINGS_PATH = get_filepath("settings.json")
