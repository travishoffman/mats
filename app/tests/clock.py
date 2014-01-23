from libs.clock import Clock
from mock import Mock, patch, create_autospec, call
import unittest
import datetime

class ClockTest(unittest.TestCase):
	def test_is_market_open(self):
		new_years = datetime.datetime(2014, 1, 1, 15)
		non_holiday = datetime.datetime(2014, 1, 2, 15)
		before_open = datetime.datetime(2014, 1, 2, 14, 29)
		at_open = datetime.datetime(2014, 1, 2, 14, 30)
		before_close = datetime.datetime(2014, 1, 2, 20, 59)
		at_close = datetime.datetime(2014, 1, 2, 21)

		clock = Clock()
		self.assertFalse(clock.is_market_open(new_years))
		self.assertTrue(clock.is_market_open(non_holiday))
		self.assertFalse(clock.is_market_open(before_open))
		self.assertTrue(clock.is_market_open(at_open))
		self.assertTrue(clock.is_market_open(before_close))
		self.assertFalse(clock.is_market_open(at_close))