from libs.ticker import Ticker
from libs.quote import Quote
from libs.trade import Trade
from mock import Mock, patch, create_autospec
import httplib
import unittest

class TestTicker(unittest.TestCase):
	def test_status_handler(self):
		ticker = Ticker()
		ticker.logger.info = Mock()
		
		data = {'status': 'connected'}
		ticker.status_handler(data)
		ticker.logger.info.assert_called_with('connected to stream')

		data = {'status': 'disconnected'}
		ticker.status_handler(data)		
		ticker.logger.info.assert_called_with('disconnected from stream')

	@patch('libs.ticker.Quote')
	def test_quote_handler(self, mock):
		ticker = Ticker()
		
		data1 = {
			'quote': {
				'bid': '539.53', 
				'qcond': 'Regular, two-sided open quote automated',
				'asksz': '2',
				'symbol': 'AAPL',
				'exch': 'NASDAQ Regional/CTS'
			}
		}

		data2 = {
			'quote': {
				'bidsz': '1', 
				'bid': '539.53', 
				'qcond': 'Regular, two-sided open quote automated',
				'ask': '539.65',
				'asksz': '2',
				'symbol': 'AAPL',
				'exch': 'NASDAQ Regional/CTS'
			}
		}
		
		ticker.tk.get_quotes = Mock(return_value=data2)
		mock_quote = Quote(data1['quote'])
		mock_quote.save = Mock(return_value=0)
		mock_quote.merge = Mock(return_value=0)
		mock.return_value = mock_quote

		ticker.quote_handler(data1)
		self.assertEqual(mock.call_count, 1)
		self.assertEqual(ticker.tk.get_quotes.call_count, 1)
		self.assertEqual(mock_quote.merge.call_count, 1)

		mock_quote.is_complete = Mock(return_value=True)
		ticker.quote_handler(data1)
		self.assertEqual(mock.call_count, 2)
		self.assertEqual(mock_quote.merge.call_count, 2)

	@patch('libs.ticker.Trade')
	def test_trade_handler(self, mock):
		ticker = Ticker()
		
		data1 = {
			u'trade': {
				u'last': u'539.819',
				u'tcond': u'9',
				u'symbol': u'AAPL',
				u'vwap': u'536.1819',
				u'datetime': u'2014-01-13T10:59:22-05:00',
				u'cvol': u'4693625',
				u'timestamp': u'1389628762',
				u'exch': u'NYSE Trade Reporting Facility'
			}
		}

		data2 = {
			u'trade': {
				u'last': u'539.819',
				u'tcond': u'9',
				u'symbol': u'AAPL',
				u'vl': u'75',
				u'vwap': u'536.1819',
				u'datetime': u'2014-01-13T10:59:22-05:00',
				u'cvol': u'4693625',
				u'timestamp': u'1389628762',
				u'exch': u'NYSE Trade Reporting Facility'
			}
		}

		data3 = {
			'quote': {
				'bidsz': '1', 
				'bid': '539.53', 
				'qcond': 'Regular, two-sided open quote automated',
				'ask': '539.65',
				'asksz': '2',
				'symbol': 'AAPL',
				'exch': 'NASDAQ Regional/CTS'
			}
		}
		
		ticker.tk.get_quotes = Mock(return_value=data3)
		mock_trade = Trade(data1['trade'])
		mock_trade.save = Mock(return_value=0)
		mock_trade.merge = Mock(return_value=0)
		mock.return_value = mock_trade

		ticker.trade_handler(data1)
		self.assertEqual(mock.call_count, 1)
		self.assertEqual(ticker.tk.get_quotes.call_count, 1)
		self.assertEqual(mock_trade.merge.call_count, 1)

		mock_trade.is_complete = Mock(return_value=True)
		ticker.trade_handler(data1)
		self.assertEqual(mock.call_count, 2)
		self.assertEqual(mock_trade.merge.call_count, 2)

	def test_start(self):
		ticker = Ticker()

		watchlist_data = [{ 'symbol': 'AAPL' }]
		ticker.watchlist.get = Mock(return_value=watchlist_data)
		ticker.stream = Mock(return_value=0)
		ticker.handle_stream_exception = Mock(return_value=0)

		ticker.start()
		ticker.stream.assert_called_with(['AAPL'])

		ticker.stream.side_effect = httplib.IncompleteRead('test')
		ticker.start()
		self.assertEqual(ticker.handle_stream_exception.call_count, 1)