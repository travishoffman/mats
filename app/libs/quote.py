from stream_data import StreamData
import time

class Quote(StreamData):
	def __init__(self, data):
		data['ts'] = time.time()
		fields = ['ask', 'asksz', 'bid', 'bidsz', 'exch', 'qcond', 'symbol', 'ts']
		StreamData.__init__(self, fields, data)
		self.quotes = self.db.quotes

	def save(self):
		return self.quotes.insert(self._data)