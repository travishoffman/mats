from stream_data import StreamData
import copy

class Trade(StreamData):
	def __init__(self, data):
		fields = ['symbol', 'exch', 'last', 'vl', 'vwap', 'cvol', 'tcond']
		StreamData.__init__(self, fields, data)
		self.trades = self.db.trades

	def save(self):
		self.trades.insert(self._data)