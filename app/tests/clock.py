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
		seven_secs_before = datetime.datetime(2014, 1, 2, 14, 29, 23)
		eleven_secs_before = datetime.datetime(2014, 1, 2, 14, 29, 19)

		clock = Clock()
		self.assertFalse(clock.is_market_open(new_years))
		self.assertTrue(clock.is_market_open(non_holiday))
		self.assertFalse(clock.is_market_open(before_open))
		self.assertTrue(clock.is_market_open(at_open))
		self.assertTrue(clock.is_market_open(before_close))
		self.assertFalse(clock.is_market_open(at_close))
		self.assertTrue(clock.is_market_open(seven_secs_before))
		self.assertFalse(clock.is_market_open(eleven_secs_before))

	def test_next_market_open(self):
		new_years_before = datetime.datetime(2014, 1, 1, 8)
		new_years_during = datetime.datetime(2014, 1, 1, 15)
		new_years_after = datetime.datetime(2014, 1, 1, 23)
		friday_after = datetime.datetime(2014, 1, 24, 23)
		saturday_before = datetime.datetime(2014, 1, 25, 9)
		saturday_during = datetime.datetime(2014, 1, 25, 16)
		saturday_after = datetime.datetime(2014, 1, 25, 23)
		market_day_before = datetime.datetime(2014, 1, 27, 9)
		market_day_open = datetime.datetime(2014, 1, 27, 14, 30)
		market_day_during = datetime.datetime(2014, 1, 27, 16)
		market_day_close = datetime.datetime(2014, 1, 27, 21)
		market_day_after = datetime.datetime(2014, 1, 27, 23)

		clock = Clock()
		next = clock.next_market_open(new_years_before)
		self.assertEquals(next, datetime.datetime(2014, 1, 2, 14, 30))
		next = clock.next_market_open(new_years_during)
		self.assertEquals(next, datetime.datetime(2014, 1, 2, 14, 30))
		next = clock.next_market_open(new_years_after)
		self.assertEquals(next, datetime.datetime(2014, 1, 2, 14, 30))
		next = clock.next_market_open(friday_after)
		self.assertEquals(next, datetime.datetime(2014, 1, 27, 14, 30))
		next = clock.next_market_open(saturday_before)
		self.assertEquals(next, datetime.datetime(2014, 1, 27, 14, 30))
		next = clock.next_market_open(saturday_after)
		self.assertEquals(next, datetime.datetime(2014, 1, 27, 14, 30))
		next = clock.next_market_open(market_day_before)
		self.assertEquals(next, datetime.datetime(2014, 1, 27, 14, 30))
		next = clock.next_market_open(market_day_open)
		self.assertEquals(next, datetime.datetime(2014, 1, 28, 14, 30))
		next = clock.next_market_open(market_day_during)
		self.assertEquals(next, datetime.datetime(2014, 1, 28, 14, 30))
		next = clock.next_market_open(market_day_close)
		self.assertEquals(next, datetime.datetime(2014, 1, 28, 14, 30))
		next = clock.next_market_open(market_day_after)
		self.assertEquals(next, datetime.datetime(2014, 1, 28, 14, 30))

	def test_secs_until_open(self):
		thursday_after = datetime.datetime(2014, 1, 23, 23)
		friday_after = datetime.datetime(2014, 1, 24, 23)
		
		clock = Clock()
		secs = clock.secs_until_open(thursday_after)
		self.assertEquals(secs, 55800) # 15.5 hours
		secs = clock.secs_until_open(friday_after)
		self.assertEquals(secs, 228600) # 2 days 15.5 hours
		
