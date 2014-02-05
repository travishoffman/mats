from ticker import Ticker
from clock import Clock
from multiprocessing import Process, Pipe
import logging
import time

class TheLoop:
	def __init__(self):
		self.clock = Clock()
		self.logger = logging.getLogger('mats')
		self.accepting_new_quote = True
		self.accepting_new_trade = True
		self.ticker_handlers = {
			'incomplete_read': self.incomplete_read_handler,
			'ssl_error':  self.ssl_error_handler,
			'unknown_error': self.unknown_error_handler,
			'connected': self.connected_handler,
			'new_quote': self.new_quote_handler,
			'new_trade': self.new_trade_handler,
			'empty_watchlist': self.empty_watchlist_handler
		}

	def loop(self):
		self.ticker_p, self.ticker_conn = self.launch_ticker()
		while True:
			if not self.clock.is_market_open():
				self.logger.info('theloop: market is closed. killing ticker.')
				self.ticker_p.terminate()
				
				# block until ticker child has time to exit
				while self.ticker_p.is_alive():
					pass
				
				# now go to sleep
				self.go_to_sleep()
			elif not self.ticker_p.is_alive():
				self.ticker_p, self.ticker_conn = self.launch_ticker()

			if self.ticker_conn.poll():
				data = self.ticker_conn.recv()
				self.ticker_handlers[data.name](data)

	def ticker(self, conn):
		ticker = Ticker(conn)
		ticker.start()

	def launch_ticker(self):
		self.logger.info('theloop: spawning ticker child process')
		parent, child = Pipe()		
		p = Process(target=self.ticker, name='ticker', args=(child,))
		p.start()
		return (p, parent)

	def incomplete_read_handler(self, data):
		self.logger.error('theloop: ticker had incompleteread error, attempting to respawn ticker.')
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def ssl_error_handler(self, data):
		self.logger.error('theloop: ticker had ssl_error, attempting to respawn ticker.')
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def unknown_error_handler(self, data):
		self.logger.error('theloop: ticker had an unknown error, attempting to respawn ticker.')
		self.ticker_p, self.ticker_conn = self.launch_ticker()		

	def connected_handler(self, event):
		self.logger.info('theloop: ticker connected to stream')

	def go_to_sleep(self):
		secs = self.clock.secs_until_open()
		time_slept = time.time()

		self.logger.info('theloop: sleeping for ' + str(secs) + ' seconds.')
		time.sleep(secs)

		secs_asleep = time.time() - time_slept
		self.logger.info('theloop: waking up after ' + str(secs_asleep) + ' seconds')
		self.logger.info('theloop: attempting to respawn ticker.')

		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def new_quote_handler(self, event):
		self.logger.debug('theloop: ticker reports new quote')

	def new_trade_handler(self, event):
		self.logger.debug('theloop: ticker reports new trade')

	def empty_watchlist_handler(self, event):
		self.logger.info('theloop: exiting.')
		exit(0)