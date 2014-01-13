from libs.stream_data import StreamData
import unittest

class TestStreamData(unittest.TestCase):
	def setUp(self):
		self.fields = ['ask', 'bid', 'bidsz', 'exch', 'qcond', 'symbol']

	def test_weed(self):
		data = {
			u'bidsz': u'1', 
			u'bid': u'539.53', 
			u'qcond': u'Regular, two-sided open quote automated', 
			u'ask': u'539.65', 
			u'asksz': u'2', 
			u'symbol': u'AAPL', 
			u'exch': u'NASDAQ Regional/CTS'
		}
		self.assertEqual(len(data), 7)
		sd = StreamData(self.fields, data)
		self.assertEqual(len(sd._data), len(sd._fields))

	def test_merge(self):
		data1 = {
			u'bidsz': u'1', 
			u'bid': u'539.53',
			u'symbol': u'AAPL', 
			u'exch': u'NASDAQ Regional/CTS'
		}
		data2 = {
			u'bidsz': u'3', 
			u'qcond': u'test'
		}
		data3 = {
			u'bidsz': u'3', 
			u'bid': u'539.53',
			u'symbol': u'AAPL', 
			u'exch': u'NASDAQ Regional/CTS',
			u'qcond': u'test'
		}

		sd = StreamData(self.fields, data1)
		data4 = sd.merge(data2)
		shared_items = set(data4.items()) - set(data3.items())
		self.assertEqual(len(shared_items), 0)

	def test_is_complete(self):
		data1 = {
			u'bidsz': u'1', 
			u'bid': u'539.53',
			u'symbol': u'AAPL', 
			u'exch': u'NASDAQ Regional/CTS'
		}
		data2 = {
			u'bidsz': u'1', 
			u'bid': u'539.53', 
			u'qcond': u'Regular, two-sided open quote automated', 
			u'ask': u'539.65', 
			u'asksz': u'2', 
			u'symbol': u'AAPL', 
			u'exch': u'NASDAQ Regional/CTS'
		}

		sd = StreamData(self.fields, data1)
		self.assertFalse(sd.is_complete())
		sd = StreamData(self.fields, data2)
		self.assertTrue(sd.is_complete())
