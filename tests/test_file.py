from datetime import datetime
import json
import os
import unittest
from unittest import mock

from plotting_tool import file
from plotting_tool.constants import (
    IDS_DEFAULT_STATE, PRICES_DEFAULT_STATE,
    BUNDLES_DEFAULT_STATE, BUNDLE_PRICES_DEFAULT_STATE
)

from tests.util import get_filepath, TEST_DATA_FOLDER


TMP_FILEPATH = get_filepath("tmp.csv")
IDS_FILEPATH = get_filepath("ids.json")
PRICES_FILEPATH = get_filepath("prices.csv")
BUNDLES_FILEPATH = get_filepath("bundles.json")
BUNDLE_PRICES_FILEPATH = get_filepath("bundle_prices.csv")

EXAMPLE_IDS = ["bitcoin", "ethereum"]
EXAMPLE_PRICES_DATA = (
    "timestamp,bitcoin,ethereum\n" +
    "2022-03-29 14:58:22.365454,47891,0\n" +
    "2022-03-29 14:59:22.365454,47892,3542\n"
)
EXAMPLE_BUNDLES = {"test": {"bitcoin": 10}}
EXAMPLE_BUNDLE_PRICES = (
    "timestamp,test\n" +
    "2022-03-29 14:58:22.365454,478910\n" +
    "2022-03-29 14:59:22.365454,478920\n"
)


def create_default_files():
    """
    Create default files for testing.
    """
    with open(IDS_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(IDS_DEFAULT_STATE)

    with open(PRICES_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(PRICES_DEFAULT_STATE)

    with open(BUNDLES_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(BUNDLES_DEFAULT_STATE)

    with open(BUNDLE_PRICES_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(BUNDLE_PRICES_DEFAULT_STATE)


def init_example_data():
    """
    Initialize example data for testing.
    """
    with open(IDS_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(EXAMPLE_IDS))

    with open(PRICES_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(EXAMPLE_PRICES_DATA)

    with open(BUNDLES_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(EXAMPLE_BUNDLES))

    with open(BUNDLE_PRICES_FILEPATH, "w", encoding="utf-8") as outfile:
        outfile.write(EXAMPLE_BUNDLE_PRICES)


@mock.patch("plotting_tool.file.TMP_FILEPATH", TMP_FILEPATH)
@mock.patch("plotting_tool.file.IDS_FILEPATH", IDS_FILEPATH)
@mock.patch("plotting_tool.file.PRICES_FILEPATH", PRICES_FILEPATH)
@mock.patch("plotting_tool.file.BUNDLES_FILEPATH", BUNDLES_FILEPATH)
@mock.patch("plotting_tool.file.BUNDLE_PRICES_FILEPATH",
            BUNDLE_PRICES_FILEPATH)
class TestFile(unittest.TestCase):
    """
    File module test class.
    """
    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(TEST_DATA_FOLDER):
            os.mkdir(TEST_DATA_FOLDER)

    @classmethod
    def tearDownClass(cls) -> None:
        for filepath in os.listdir(TEST_DATA_FOLDER):
            os.remove(get_filepath(filepath))

        os.rmdir(TEST_DATA_FOLDER)

    def test_read_csv(self) -> None:
        init_example_data()

        prices = []
        for row in EXAMPLE_PRICES_DATA.split("\n")[1:3]:
            prow = {}
            (prow["timestamp"], prow["bitcoin"], prow["ethereum"]) = \
                row.split(",")
            prices.append(prow)
        read_prices = list(file._read_csv(get_filepath(PRICES_FILEPATH)))
        self.assertEqual(prices, read_prices)

        prices = []
        for row in EXAMPLE_BUNDLE_PRICES.split("\n")[1:3]:
            prow = {}
            (prow["timestamp"], prow["test"]) = row.split(",")
            prices.append(prow)
        read_prices = list(
            file._read_csv(get_filepath(BUNDLE_PRICES_FILEPATH))
        )
        self.assertEqual(prices, read_prices)

    def test_load_prices(self) -> None:
        init_example_data()
        prices = file.load_cryptocur_prices()

        self.assertEqual(prices["bitcoin"], [47891, 47892])
        self.assertEqual(prices["ethereum"], [3542])

        example_date = prices["timestamp"][0]
        self.assertEqual(example_date.day, 29)
        self.assertEqual(example_date.month, 3)
        self.assertEqual(example_date.year, 2022)
        self.assertEqual(example_date.hour, 14)
        self.assertEqual(example_date.minute, 58)

        prices = file.load_cryptocur_prices(["bitcoin"])
        self.assertEqual(prices["bitcoin"], [47891, 47892])

        with self.assertRaises(KeyError):
            self.assertEqual(prices["ethereum"], [3542])

        example_date = prices["timestamp"][0]
        self.assertEqual(example_date.day, 29)
        self.assertEqual(example_date.month, 3)
        self.assertEqual(example_date.year, 2022)
        self.assertEqual(example_date.hour, 14)
        self.assertEqual(example_date.minute, 58)

    def test_load_cryptocur_statistics(self) -> None:
        init_example_data()

        statistics = file.load_cryptocur_statistics()
        self.assertEqual(statistics["bitcoin"]["min"], 47891)
        self.assertEqual(statistics["bitcoin"]["max"], 47892)
        self.assertEqual(statistics["bitcoin"]["mean"], (47891 + 47892) / 2)

        self.assertEqual(statistics["ethereum"]["min"], 3542)
        self.assertEqual(statistics["ethereum"]["max"], 3542)
        self.assertEqual(statistics["ethereum"]["mean"], 3542)

    def test_calculate_plotting_point_ratio(self) -> None:
        create_default_files()
        self.assertEqual(file.calculate_plotting_point_ratio(), 1)

        init_example_data()
        self.assertEqual(file.calculate_plotting_point_ratio(), 1)

    def test_load_cryptocur_plot_prices(self) -> None:
        create_default_files()
        self.assertEqual({"timestamp": []}, file.load_cryptocur_plot_prices())

        init_example_data()
        timestamps = [
            datetime.fromisoformat("2022-03-29 14:58:22.365454"),
            datetime.fromisoformat("2022-03-29 14:59:22.365454")
        ]
        self.assertEqual(
            {
                "timestamp": timestamps,
                "bitcoin": [47891.0, 47892.0],
                "ethereum": [3542.0]
            },
            file.load_cryptocur_plot_prices()
        )

        # Fail if try to load non-existing cryptocurrency.
        with self.assertRaises(KeyError):
            file.load_cryptocur_plot_prices(["cardano"])

    def test_load_bundle_plot_prices(self) -> None:
        create_default_files()
        self.assertEqual({"timestamp": []}, file.load_bundle_plot_prices())

        init_example_data()
        timestamps = [
            datetime.fromisoformat("2022-03-29 14:58:22.365454"),
            datetime.fromisoformat("2022-03-29 14:59:22.365454")
        ]
        self.assertEqual(
            {"timestamp": timestamps, "test": [478910, 478920]},
            file.load_bundle_plot_prices()
        )

        # Fail if try to load non-existing cryptocurrency.
        with self.assertRaises(KeyError):
            file.load_bundle_plot_prices(["example_name"])

    def test_get_csv_line_count(self) -> None:
        create_default_files()
        self.assertEqual(
            0, file.get_csv_line_count(get_filepath(PRICES_FILEPATH)))
        self.assertEqual(
            0, file.get_csv_line_count(get_filepath(BUNDLE_PRICES_FILEPATH)))

        init_example_data()
        self.assertEqual(
            2, file.get_csv_line_count(get_filepath(PRICES_FILEPATH)))
        self.assertEqual(
            2, file.get_csv_line_count(get_filepath(BUNDLE_PRICES_FILEPATH)))

    def test_load_bundles(self) -> None:
        create_default_files()
        self.assertEqual(file.load_bundles(), {})

        init_example_data()
        self.assertEqual(file.load_bundles(), {"test": {"bitcoin": 10}})

    def test_load_bundle_ids(self) -> None:
        create_default_files()
        self.assertEqual(file.load_bundle_ids(), [])

        init_example_data()
        self.assertEqual(file.load_bundle_ids(), ["test"])

    def test_load_bundle(self) -> None:
        init_example_data()

        with self.assertRaises(ValueError):
            file.load_bundle("example_name")

        file.create_bundle("test1")
        self.assertEqual(file.load_bundle("test1"), {})

        init_example_data()
        self.assertEqual(file.load_bundle("test"), {"bitcoin": 10})

    def test_valid_bundle_ids(self) -> None:
        create_default_files()
        self.assertFalse(file.valid_bundle_ids(["test"]))
        self.assertFalse(file.valid_bundle_ids(["othertest"]))
        self.assertFalse(file.valid_bundle_ids(["anothertest"]))

        init_example_data()
        self.assertTrue(file.valid_bundle_ids(["test"]))
        self.assertFalse(file.valid_bundle_ids(["othertest"]))
        file.create_bundle("othertest")
        self.assertTrue(file.valid_bundle_ids(["othertest"]))
        self.assertFalse(file.valid_bundle_ids(["anothertest"]))

    def test_create_bundle(self) -> None:
        init_example_data()
        file.create_bundle("test1")

        with open(get_filepath(BUNDLES_FILEPATH)) as infile:
            self.assertEqual(
                json.loads(infile.read()),
                {"test1": {}, "test": {"bitcoin": 10}}
            )

        with self.assertRaises(ValueError):
            file.create_bundle("test1")

    def test_add_cryptocur_to_bundle(self) -> None:
        create_default_files()

        with self.assertRaises(ValueError):
            file.add_cryptocur_to_bundle("test", "bitcoin", 1)

        init_example_data()
        file.add_cryptocur_to_bundle("test", "bitcoin", 100)
        self.assertEqual(file.load_bundle("test"), {"bitcoin": 100})
        self.assertEqual(
            file.load_bundle_plot_prices(["test"])["test"],
            [4789100.0, 4789200.0]
        )
        with self.assertRaises(ValueError):
            file.add_cryptocur_to_bundle("test", "bitc0in", 1)

    def test_remove_cryptocur_from_bundle(self) -> None:
        create_default_files()

        with self.assertRaises(ValueError):
            file.remove_cryptocur_from_bundle("test", "bitcoin")

        init_example_data()
        with self.assertRaises(ValueError):
            file.remove_cryptocur_from_bundle("test", "bitc0in")

        file.remove_cryptocur_from_bundle("test", "bitcoin")
        self.assertEqual(file.load_bundle("test"), {})
        self.assertEqual(
            file.load_bundle_plot_prices(["test"])["test"], [])

        with self.assertRaises(ValueError):
            file.remove_cryptocur_from_bundle("test", "bitcoin")

    def test_delete_bundle(self) -> None:
        init_example_data()

        with self.assertRaises(ValueError):
            file.delete_bundle("example_name")

        self.assertEqual(file.load_bundles(), {"test": {"bitcoin": 10}})
        file.create_bundle("test1")
        self.assertEqual(
            file.load_bundles(), {"test": {"bitcoin": 10}, "test1": {}})
        file.delete_bundle("test")
        self.assertEqual(file.load_bundles(), {"test1": {}})
        file.delete_bundle("test1")
        self.assertEqual(file.load_bundles(), {})

    def test_exists_in_bundles(self) -> None:
        init_example_data()
        self.assertFalse(file.exists_in_bundles("cardano"))
        self.assertFalse(file.exists_in_bundles("ethereum"))
        self.assertTrue(file.exists_in_bundles("bitcoin"))
        file.delete_bundle("test")
        self.assertFalse(file.exists_in_bundles("bitcoin"))

    def test_load_cryptocurrency_ids(self) -> None:
        create_default_files()
        self.assertEqual(file.load_cryptocurrency_ids(), [])

        init_example_data()
        self.assertEqual(
            file.load_cryptocurrency_ids(),
            ["bitcoin", "ethereum"]
        )

        file.remove_cryptocurrency("ethereum")
        self.assertEqual(file.load_cryptocurrency_ids(), ["bitcoin"])

    def test_valid_cryptocurrency_ids(self) -> None:
        init_example_data()

        self.assertTrue(file.valid_cryptocurrency_ids(["bitcoin", "ethereum"]))
        self.assertFalse(file.valid_cryptocurrency_ids(["cardano"]))
        file.delete_bundle("test")
        file.remove_cryptocurrency("bitcoin")
        self.assertFalse(file.valid_cryptocurrency_ids(["bitcoin"]))
        file.add_new_cryptocurrency("cardano")
        self.assertTrue(file.valid_cryptocurrency_ids(["cardano"]))

    def test_add_new_currency(self) -> None:
        create_default_files()
        new_cur = file.add_new_cryptocurrency("bitcoin")
        self.assertEqual(new_cur, ["bitcoin"])

        with self.assertRaises(ValueError):
            file.add_new_cryptocurrency("bitcoin")

        with open(get_filepath(IDS_FILEPATH)) as infile:
            self.assertEqual(json.loads(infile.read()), ["bitcoin"])

        with open(get_filepath(PRICES_FILEPATH)) as infile:
            self.assertEqual(infile.read(), "timestamp,bitcoin\n")

        init_example_data()
        new_cur = file.add_new_cryptocurrency("cardano")

        with open(get_filepath(IDS_FILEPATH)) as infile:
            self.assertEqual(
                json.loads(infile.read()), ["bitcoin", "ethereum", "cardano"])

        with open(get_filepath(PRICES_FILEPATH)) as infile:
            self.assertEqual(
                infile.read(),
                "timestamp,bitcoin,ethereum,cardano\n" +
                "2022-03-29 14:58:22.365454,47891,0,0\n" +
                "2022-03-29 14:59:22.365454,47892,3542,0\n")

    def test_remove_currency(self) -> None:
        init_example_data()
        new_cur = file.remove_cryptocurrency("ethereum")
        self.assertEqual(new_cur, ["bitcoin"])

        with self.assertRaises(ValueError):
            file.remove_cryptocurrency("ethereum")

        with open(get_filepath(IDS_FILEPATH)) as infile:
            self.assertEqual(json.loads(infile.read()), ["bitcoin"])

        with open(get_filepath(PRICES_FILEPATH)) as infile:
            self.assertEqual(
                infile.read(),
                "timestamp,bitcoin\n" +
                "2022-03-29 14:58:22.365454,47891\n" +
                "2022-03-29 14:59:22.365454,47892\n")

    def test_write_cryptocur_prices_entry(self) -> None:
        create_default_files()
        timestamp = datetime.now()
        file.write_cryptocur_prices_entry({"timestamp": timestamp})

        with open(get_filepath(PRICES_FILEPATH)) as infile:
            self.assertEqual(infile.read(), f"timestamp\n{timestamp}\n")

        init_example_data()

        with self.assertRaises(ValueError):
            file.write_cryptocur_prices_entry({"timestamp": timestamp})

        file.write_cryptocur_prices_entry(
            {"timestamp": timestamp, "bitcoin": 100, "ethereum": 100})
        with open(get_filepath(PRICES_FILEPATH)) as infile:
            self.assertEqual(
                infile.read(),
                "timestamp,bitcoin,ethereum\n" +
                "2022-03-29 14:58:22.365454,47891,0\n" +
                "2022-03-29 14:59:22.365454,47892,3542\n" +
                f"{timestamp},100,100\n")

    def test_write_bundle_prices_entry(self) -> None:
        create_default_files()
        timestamp = datetime.now()
        file.write_bundle_prices_entry({"timestamp": timestamp})

        with open(get_filepath(BUNDLE_PRICES_FILEPATH)) as infile:
            self.assertEqual(infile.read(), f"timestamp\n{timestamp}\n")

        init_example_data()

        with self.assertRaises(ValueError):
            file.write_cryptocur_prices_entry({"timestamp": timestamp})

        file.write_bundle_prices_entry(
            {"timestamp": timestamp, "bitcoin": 100})
        with open(get_filepath(BUNDLE_PRICES_FILEPATH)) as infile:
            self.assertEqual(
                infile.read(),
                "timestamp,test\n" +
                "2022-03-29 14:58:22.365454,478910\n" +
                "2022-03-29 14:59:22.365454,478920\n" +
                f"{timestamp},1000.0\n")


if __name__ == "__main__":
    unittest.main()
