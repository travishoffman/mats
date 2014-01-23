import datetime
import pytz
from pytz import timezone

class Clock:
	def __init__(self):
		self.tz = timezone('US/Eastern')
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

	def est_hour_min(self, date=datetime.datetime.now()):
		est_dt = self.tz.localize(date)
		date = str(est_dt).split(' ')[0]
		year, month, day = date.split('-')
		time, offset = str(est_dt).split(' ')[1].split('-')
		hour, minute, sec = time.split(':')
		offset_hour = offset.split(':')[0]
		real_hour = (int(hour) - int(offset_hour))

		return (real_hour, int(minute))

	def is_weekday(self, date=datetime.datetime.now().date()):
		if date.weekday() < 5:
			return True

		return False

	def is_holiday(self, date=datetime.datetime.now().date()):
		if date in self.market_holidays:
			return True

		return False

	def is_market_hours(self, date=datetime.datetime.now()):
		hour, minute = self.est_hour_min(date)		
		if (hour == 9 and minute >= 30):
			return True
		elif hour > 9 and hour < 16:
			return True

		return False

	def is_market_open(self, datetime=datetime.datetime.now()):
		if not self.is_holiday(datetime.date()):
			if self.is_weekday(datetime.date()) and self.is_market_hours(datetime):
				return True

		return False