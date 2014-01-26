from ticker import Ticker
from multiprocessing import Process, Pipe
import logging
import multiprocessing
import json

class TheLoop:
	def __init__(self):
		self.logger = logging.getLogger('mats')
		self.accepting_new_quote = True
		self.accepting_new_trade = True
		self.ticker_handlers = {
			'incomplete_read': self.incomplete_read_handler,
			'ssl_error':  self.ssl_error_handler,
			'connected': self.connected_handler
		}

	def loop(self):
		self.ticker_p, self.ticker_conn = self.launch_ticker()
		while True:
			if self.ticker_conn.poll():
				data = json.loads(self.ticker_conn.recv())
				self.ticker_handlers[data['data']]()

	def ticker(self, conn):
		ticker = Ticker(conn)
		ticker.start()

	def launch_ticker(self):
		self.logger.info('theloop: forking ticker child process')
		parent, child = Pipe()		
		p = Process(target=self.ticker, name='ticker', args=(child,))
		p.start()
		return (p, parent)

	def incomplete_read_handler(self):
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def ssl_error_handler(self):
		self.logger.error('theloop: ticker had ssl_error, restarting ticker')
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def connected_handler(self):
		self.logger.info('theloop: ticker connected to stream')

	def new_quote_handler(self):
		self.accepting_new_quote = False
		self.logger.debug('theloop: ticker reports new quote')

	def new_trade_handler(self):
		self.accepting_new_trade = False
		self.logger.debug('theloop: ticker reports new trade')		