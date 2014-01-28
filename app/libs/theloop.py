from ticker import Ticker
from clock import Clock
from multiprocessing import Process, Pipe
import logging
import multiprocessing
import json
import time

class TheLoop:
	def __init__(self):
		self.logger = logging.getLogger('mats')
		self.accepting_new_quote = True
		self.accepting_new_trade = True
		self.ticker_handlers = {
			'incomplete_read': self.incomplete_read_handler,
			'ssl_error':  self.ssl_error_handler,
			'connected': self.connected_handler,
			'market_closed': self.market_closed_handler,
			'new_quote': self.new_quote_handler,
			'new_trade': self.new_trade_handler,
			'empty_watchlist': self.empty_watchlist_handler
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
		self.logger.info('theloop: spawning ticker child process')
		parent, child = Pipe()		
		p = Process(target=self.ticker, name='ticker', args=(child,))
		p.start()
		return (p, parent)

	# def analyst(self, conn):
	# 	analyst = Analyst(conn)
	# 	analyst.start()

	# def launch_analyst(self):
	# 	self.logger.info('theloop: spawning analyst child process')
	# 	parent, child = Pipe()
	# 	p = Process(target=self.analyst, name='analyst', args=(child,))
	# 	p.start()
	# 	return (p, parent)

	def incomplete_read_handler(self):
		self.logger.error('theloop: ticker had incompleteread error, attempting to respawn ticker.')
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def ssl_error_handler(self):
		self.logger.error('theloop: ticker had ssl_error, attempting to respawn ticker.')
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def connected_handler(self):
		self.logger.info('theloop: ticker connected to stream')

	def market_closed_handler(self):
		clock = Clock()
		secs = clock.secs_until_open()
		time_slept = time.time()

		self.logger.info('theloop: sleeping for ' + str(secs) + ' seconds.')
		time.sleep(secs)

		time_woke = time.time()
		secs_asleep = time_woke - time_slept
		self.logger.info('theloop: waking up after ' + str(secs_asleep) + ' seconds')
		self.logger.info('theloop: attempting to respawn ticker.')
		self.ticker_p, self.ticker_conn = self.launch_ticker()

	def new_quote_handler(self):
		self.logger.debug('theloop: ticker reports new quote')


	def new_trade_handler(self):
		self.logger.debug('theloop: ticker reports new trade')

	def empty_watchlist_handler(self):
		self.logger.info('theloop: exiting.')
		exit(0)	