from dblayer import DbLayer

class WatchList(DbLayer):
	def __init__(self):
		DbLayer.__init__(self)
		self.watchlist = self.db.watchlist

	def add(self, symbol):
		self.watchlist.insert({'symbol': symbol.upper()})

	def remove(self, symbol):
		self.watchlist.remove({'symbol': symbol.upper()})

	def get(self):
		return self.watchlist.find()
