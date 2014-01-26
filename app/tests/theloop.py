from libs.theloop import TheLoop
from mock import Mock, patch, create_autospec, call
from helpers.errorafter import ErrorAfter
import unittest
import json

class TestTheLoop(unittest.TestCase):
	def test_loop(self):
		theloop = TheLoop()
		ticker_conn = Mock()
		ticker_conn.poll = Mock(return_value=True)
		ticker_conn.poll.side_effect = ErrorAfter(2)

		theloop.connected_handler = Mock(return_value=True)
		theloop.launch_ticker = Mock(return_value=(Mock(), ticker_conn))
		theloop.new_trade_handler = Mock(return_value=True)
		theloop.new_quote_handler = Mock(return_value=True)
		theloop.incomplete_read_handler = Mock(return_value=True)
		theloop.ssl_error_handler = Mock(return_value=True)
		
		with self.assertRaises(Exception):
			ticker_conn.recv = Mock(return_value={'type': 'event', 'data': 'connected'})
			theloop.loop()
			theloop.connected_handler.assert_called_once()
			
			ticker_conn.recv = Mock(return_value=json.dumps({'type': 'error', 'data': 'ssl_error'}))
			theloop.loop()
			theloop.ssl_error_handler.assert_called_once()
			
			ticker_conn.recv = Mock(return_value=json.dumps({'type': 'error', 'data': 'incomplete_read'}))
			theloop.loop()
			theloop.incomplete_read_handler.assert_called_once()

			ticker_conn.recv = Mock(return_value=json.dumps({'type': 'event', 'data': 'new_quote'}))
			theloop.loop()
			theloop.new_quote_handler.assert_called_once()

			ticker_conn.recv = Mock(return_value=json.dumps({'type': 'event', 'data': 'new_trade'}))
			theloop.loop()
			theloop.new_trade_handler.assert_called_once()