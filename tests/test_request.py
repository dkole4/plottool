import unittest

from plotting_tool import request


class TestRequest(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_fetch_data(self) -> None:
        data = request.fetch_data(["bitcoin"])

        self.assertTrue("bitcoin" in data.keys())
        self.assertTrue(data["bitcoin"]["usd"] > 0)

        data = request.fetch_data(["123"])

        self.assertEqual(data, None)

    def test_check_currency_existence(self) -> None:
        self.assertTrue(request.check_cryptocurrency_existence("bitcoin"))
        self.assertTrue(request.check_cryptocurrency_existence("ethereum"))
        self.assertTrue(request.check_cryptocurrency_existence("cardano"))

        self.assertFalse(request.check_cryptocurrency_existence("123"))
        self.assertFalse(request.check_cryptocurrency_existence("asdbv"))
        self.assertFalse(request.check_cryptocurrency_existence("1as123"))

    def test_check_vs_currency_existence(self) -> None:
        self.assertTrue(request.check_vs_currency_existence("usd"))
        self.assertTrue(request.check_vs_currency_existence("eur"))
        self.assertTrue(request.check_vs_currency_existence("gbp"))

        self.assertFalse(request.check_vs_currency_existence("asd"))
        self.assertFalse(request.check_vs_currency_existence("123"))
        self.assertFalse(request.check_vs_currency_existence("qqq"))


if __name__ == "__main__":
    unittest.main()
