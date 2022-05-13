import os
import json
import unittest
from unittest import mock

from plotting_tool import plot
from plotting_tool import settings
from plotting_tool.constants import SETTINGS_DEFAULT_STATE

from tests.util import TEST_DATA_FOLDER, SETTINGS_PATH, get_filepath


class TestPlot(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Create a mock data file folder.
        if not os.path.exists(TEST_DATA_FOLDER):
            os.mkdir(TEST_DATA_FOLDER)

        # Create a mock settings file.
        if not os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "w", encoding="utf-8") as settings:
                settings.write(json.dumps(SETTINGS_DEFAULT_STATE))

    @classmethod
    def tearDownClass(cls) -> None:
        # Remove all the mock files and directories after tests.
        for filepath in os.listdir(TEST_DATA_FOLDER):
            os.remove(get_filepath(filepath))

        os.rmdir(TEST_DATA_FOLDER)

    def test_validate_arguments(self) -> None:
        self.assertTrue(plot.valid_plot_arguments(1, 1))
        self.assertTrue(plot.valid_plot_arguments(2, 1))
        self.assertTrue(plot.valid_plot_arguments(2, 2))
        self.assertTrue(plot.valid_plot_arguments(4, 4))

        self.assertFalse(plot.valid_plot_arguments(1, 0))
        self.assertFalse(plot.valid_plot_arguments(3, 1))
        self.assertFalse(plot.valid_plot_arguments(10, 5))
        self.assertFalse(plot.valid_plot_arguments(1, 16))
        self.assertFalse(plot.valid_plot_arguments(1, -1))

    def test_check_price_range(self) -> None:
        with mock.patch("plotting_tool.settings.SETTINGS_PATH",
                        SETTINGS_PATH):
            mock_setting_handler = settings.SettingHandler()

            with mock.patch("plotting_tool.plot.SettingHandler",
                            return_value=mock_setting_handler):
                self.assertTrue(plot.check_price_range(0.5, 0.5))
                self.assertTrue(plot.check_price_range(0.8, 1))
                self.assertTrue(plot.check_price_range(1, 0.8))
                self.assertFalse(plot.check_price_range(0.5, 0.0001))
                self.assertFalse(plot.check_price_range(0.0001, 0.5))
                self.assertFalse(plot.check_price_range(0.5, 100))
                self.assertFalse(plot.check_price_range(100, 0.5))


if __name__ == "__main__":
    unittest.main()
