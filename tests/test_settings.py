import os
import json
import unittest
from unittest import mock

from plotting_tool import settings
from plotting_tool.constants import SETTING, SETTINGS_DEFAULT_STATE

from tests.util import TEST_DATA_FOLDER, SETTINGS_PATH, get_filepath


@mock.patch("plotting_tool.settings.SETTINGS_PATH", SETTINGS_PATH)
class TestSettings(unittest.TestCase):
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

    def test_read_field(self) -> None:
        handler = settings.SettingHandler()
        self.assertIsNotNone(handler.read_field(SETTING.USE_TIME))
        self.assertIsNotNone(handler.read_field(SETTING.VS_CURRENCY))
        self.assertIsNotNone(handler.read_field(SETTING.SAME_LIMITS_THRESHOLD))

    def test_set_field(self) -> None:
        handler = settings.SettingHandler()

        handler.set_field(SETTING.USE_TIME, False)
        self.assertEqual(handler.read_field(SETTING.USE_TIME), False)
        handler.set_field(SETTING.USE_TIME, True)
        self.assertEqual(handler.read_field(SETTING.USE_TIME), True)

        with self.assertRaises(ValueError):
            handler.set_field(SETTING.USE_TIME, True, True)

        handler.set_field(SETTING.VS_CURRENCY, "eur")
        self.assertEqual(handler.read_field(SETTING.VS_CURRENCY), "eur")
        handler.set_field(SETTING.VS_CURRENCY, "gbp")
        self.assertEqual(handler.read_field(SETTING.VS_CURRENCY), "gbp")

        with self.assertRaises(ValueError):
            handler.set_field(SETTING.VS_CURRENCY, True, True)

        handler.set_field(SETTING.SAME_LIMITS_THRESHOLD, 2)
        self.assertEqual(handler.read_field(SETTING.SAME_LIMITS_THRESHOLD), 2)
        handler.set_field(SETTING.SAME_LIMITS_THRESHOLD, 1.1, True)
        self.assertEqual(
            handler.read_field(SETTING.SAME_LIMITS_THRESHOLD), 1.1)

        with self.assertRaises(ValueError):
            handler.set_field(SETTING.SAME_LIMITS_THRESHOLD, "asd")

        with self.assertRaises(ValueError):
            handler.set_field(SETTING.SAME_LIMITS_THRESHOLD, -1)

    def test_get_setting_repr(self) -> None:
        handler = settings.SettingHandler()

        setting_repr = handler.get_setting_repr()
        self.assertTrue("use_time" in setting_repr)
        self.assertTrue("vs_currency" in setting_repr)
        self.assertTrue("same_limits_threshold" in setting_repr)


if __name__ == "__main__":
    unittest.main()
