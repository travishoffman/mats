from dblayer import DbLayer
import logging

class WatchList(DbLayer):
	def __init__(self):
		self.logger = logging.getLogger('mats')
		DbLayer.__init__(self)
		self.watchlist = self.db.watchlist

	def add(self, symbol):
		self.watchlist.insert({'symbol': symbol.upper()})

	def remove(self, symbol):
		self.logger.info('removing ' + symbol + ' from watchlist')
		self.watchlist.remove({'symbol': symbol.upper()})

	def get(self):
		return self.watchlist.find()