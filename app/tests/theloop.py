from libs.theloop import TheLoop
from libs.event import Event, QuoteEvent, StatusEvent, TradeEvent
from mock import Mock, patch, call
import unittest
import json

class TheLoopTest(unittest.TestCase):
	def test_loop_iter(self):
		theloop = TheLoop()
		ticker_conn = Mock()
		ticker_conn.poll = Mock(return_value=True)

		theloop.clock.is_market_open = Mock(return_value=True)
		theloop.connected_handler = Mock(return_value=True)
		theloop.launch_ticker = Mock(return_value=(Mock(), ticker_conn))
		theloop.new_trade_handler = Mock(return_value=True)
		theloop.new_quote_handler = Mock(return_value=True)
		theloop.incomplete_read_handler = Mock(return_value=True)
		theloop.ssl_error_handler = Mock(return_value=True)
		theloop.ticker_p = Mock(return_value=True)
		theloop.ticker_conn = Mock(return_value=True)
		theloop.logger = Mock(return_value=True)

		theloop.ticker_conn.recv = Mock(return_value=StatusEvent(name='connected'))
		theloop.loop_iter()
		theloop.connected_handler.assert_called_once()
			
		theloop.ticker_conn.recv = Mock(return_value=Event(name='ssl_error'))
		theloop.loop_iter()
		theloop.ssl_error_handler.assert_called_once()
			
		theloop.ticker_conn.recv = Mock(return_value=Event(name='incomplete_read'))
		theloop.loop_iter()
		theloop.incomplete_read_handler.assert_called_once()

		theloop.ticker_conn.recv = Mock(return_value=QuoteEvent(name='new_quote', object_id='abc123', symbol='AAPL'))
		theloop.loop_iter()
		theloop.new_quote_handler.assert_called_once()

		ticker_conn.recv = Mock(return_value=TradeEvent(name='new_trade', object_id='abc123', symbol='AAPL'))
		theloop.loop_iter()
		theloop.new_trade_handler.assert_called_once()