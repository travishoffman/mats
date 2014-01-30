import datetime
from datetime import timedelta
import pytz
from pytz import timezone

class Clock:
	def __init__(self):
		self.market_holidays = [
			datetime.date(2014, 1, 1),
			datetime.date(2014, 1, 20),
			datetime.date(2014, 4, 18),
			datetime.date(2014, 5, 26),
			datetime.date(2014, 7, 4),
			datetime.date(2014, 9, 1),
			datetime.date(2014, 11, 27),
			datetime.date(2014, 12, 25)
		]

	def is_weekday(self, d=datetime.datetime.now().date()):
		return d.weekday() < 5

	def is_holiday(self, d=datetime.datetime.now().date()):
		if d in self.market_holidays:
			return True

		return False

	def is_market_hours(self, d=datetime.datetime.now()):
		hour, minute, second = (d.hour, d.minute, d.second)
		tolerence = 10
		threshold = 30 - second
		if hour == 14 and (minute >= 30 or 
			(minute == 29 and threshold <= tolerence)):
			return True
		elif hour > 14 and hour < 21:
			return True

		return False

	def is_market_open(self, dt=datetime.datetime.now()):
		if not self.is_holiday(dt.date()):
			if self.is_weekday(dt.date()) and self.is_market_hours(dt):
				return True

		return False

	def is_before_open(self, dt=datetime.datetime.now()):
		if dt.hour < 14 or dt.hour == 14 and dt.minute < 30:
			return True

		return False

	def next_market_open(self, dt=datetime.datetime.now()):
		if self.is_before_open(dt):
			market_open = datetime.datetime(dt.year, dt.month, dt.day, 14, 30)
			if self.is_market_open(market_open):
				return market_open
				
		dt += timedelta(days=1)
		dt = datetime.datetime(dt.year, dt.month, dt.day, 14, 30)

		if self.is_market_open(dt):
			return dt

		return self.next_market_open(dt)

	def secs_until_open(self, dt=datetime.datetime.now()):
		diff = self.next_market_open(dt) - dt
		return diff.seconds