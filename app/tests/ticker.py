from libs.ticker import Ticker
from libs.quote import Quote
from libs.trade import Trade
from mock import Mock, patch, create_autospec, call
from multiprocessing import Process, Pipe
import httplib
import unittest
import json

class TickerTest(unittest.TestCase):
	def test_status_handler(self):
		parent, child = Pipe()
		ticker = Ticker(child)
		ticker.conn = Mock()
		ticker.conn.send = Mock()
		ticker.logger.info = Mock()
		
		data = {'status': 'connected'}
		ticker.status_handler(data)
		ticker.conn.send.assert_called_with(json.dumps({'type': 'event', 'data': 'connected'}))

		data = {'status': 'disconnected'}
		ticker.status_handler(data)		
		ticker.conn.send.assert_called_with(json.dumps({'type': 'event', 'data': 'disconnected'}))

	@patch('libs.ticker.Quote')
	def test_quote_handler(self, mock):
		parent, child = Pipe()
		ticker = Ticker(child)
		
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
		parent, child = Pipe()
		ticker = Ticker(child)
		
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
		parent, child = Pipe()
		ticker = Ticker(child)
		ticker.conn = Mock()
		ticker.conn.send = Mock()
		ticker.logger = Mock()
		ticker.clock = Mock()
		ticker.clock.is_market_open = Mock(return_value=True)
		watchlist_data = [{ 'symbol': 'AAPL' }]
		ticker.watchlist.get = Mock(return_value=watchlist_data)
		ticker.stream = Mock(return_value=0)
		ticker.handle_stream_exception = Mock(return_value=0)
		ticker.sanitize_watchlist = Mock()

		ticker.start()
		ticker.stream.assert_called_with(['AAPL'])
		self.assertTrue(ticker.sanitize_watchlist.call_count, 1)

		ticker.stream.side_effect = httplib.IncompleteRead('test')
		ticker.start()
		ticker.conn.send.assert_called_with(json.dumps({'type': 'error', 'data': 'incomplete_read'}))
		
		ticker.clock.is_market_open = Mock(return_value=False)
		ticker.start()
		ticker.conn.send.assert_called_with(json.dumps({'type': 'info', 'data': 'market_closed'}))

	def test_sanitize_watchlist(self):
		parent, child = Pipe()
		ticker = Ticker(child)
		
		ticker.logger.info = Mock()
		watchlist_data = [
			{'symbol': 'AAPL'},
			{'symbol': 'TST'}
		]
		quote_data = [
			{'symbol': 'AAPL'}
		]
		ticker.watchlist.get = Mock(return_value=watchlist_data)
		ticker.watchlist.remove = Mock()
		ticker.tk.get_quotes = Mock(return_value=None)

		ticker.sanitize_watchlist()
		self.assertEqual(ticker.watchlist.remove.call_args_list, [call('AAPL'), call('TST')])

		ticker.tk.get_quotes = Mock(return_value=quote_data)
		ticker.watchlist.remove.reset_mock()
		ticker.sanitize_watchlist()
		self.assertEqual(ticker.watchlist.remove.call_args_list, [call('TST')])