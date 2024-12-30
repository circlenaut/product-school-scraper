import unittest

from product_school_scraper.utils.helper import format_seconds

class TestFormatSeconds(unittest.TestCase):
    def test_zero_seconds(self):
        self.assertEqual(format_seconds(0), "0.00 seconds")

    def test_only_seconds(self):
        self.assertEqual(format_seconds(45), "45.00 seconds")

    def test_minutes_and_seconds(self):
        self.assertEqual(format_seconds(75), "1 minute, 15.00 seconds")

    def test_only_hours(self):
        self.assertEqual(format_seconds(3600), "1 hour, 0.00 seconds")

    def test_hours_and_minutes(self):
        self.assertEqual(format_seconds(3660), "1 hour, 1 minute, 0.00 seconds")

    def test_hours_minutes_seconds(self):
        self.assertEqual(format_seconds(3661), "1 hour, 1 minute, 1.00 second")

    def test_days_hours_minutes_seconds(self):
        self.assertEqual(format_seconds(90061), "1 day, 1 hour, 1 minute, 1.00 second")

    def test_plural_days_hours_minutes_seconds(self):
        self.assertEqual(format_seconds(172800 + 7200 + 120 + 2), "2 days, 2 hours, 2 minutes, 2.00 seconds")

if __name__ == '__main__':
    unittest.main()