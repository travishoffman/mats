from watchlist import WatchList
from quote import Quote
from trade import Trade
from tradeking import TradeKing
from clock import Clock
import sys
import logging
import httplib
import ssl

logger = logging.getLogger('mats')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

class Ticker:
	def __init__(self):
		self.logger = logging.getLogger('mats')
		self.watchlist = WatchList()
		self.quotes = {}
		self.trades = {}
		self.tk = TradeKing({
			'consumer_key': 'SmgvD5it3jrAgZ6DyQdB1rPshIDrdakEseWkaQWz',
			'consumer_secret': 'BLCTEO2O3So2sR1jQJ84u6SiSBWWNGKFgkLTlo1p',
			'oauth_token': 'DmlnWjGgW5BVWGKUMkkxMCX3UM8SsL7h3MtlqPWJ',
			'oauth_token_secret': 'DOXRh1D74wVj4F2uL7d6ZfJyh6awjoOP7WRROcTw'
		})
		self.handlers = {
			'status': self.status_handler,
			'quote': self.quote_handler,
			'trade': self.trade_handler
		}

	def status_handler(self, resp):
		if resp['status'] == 'connected':
			self.logger.info('connected to stream')
		else:
			self.logger.info('disconnected from stream')

	def quote_handler(self, resp):
		symbol = resp['quote']['symbol']
		if resp['quote']['symbol'] not in self.quotes.keys():
			q = Quote(resp['quote'])
		else:
			q = Quote(self.quotes[symbol].merge(resp['quote']))

		if q.is_complete() is False:
			quote_data = self.tk.get_quotes([symbol])
			q.merge(quote_data)

		q.save()
		self.quotes[symbol] = q

	def trade_handler(self, resp):
		symbol = resp['trade']['symbol']
		if resp['trade']['symbol'] not in self.trades.keys():
			t = Trade(resp['trade'])
		else:
			t = Trade(self.trades[symbol].merge(resp['trade']))

		if t.is_complete() is False:
			trade_data = self.tk.get_quotes([symbol])
			t.merge(trade_data)

		t.save()
		self.trades[symbol] = t

	def stream(self, watchlist_lst):
		for resp in self.tk.get_stream(watchlist_lst):
			self.handlers[resp.keys()[0]](resp)

	def start(self):
		global logger
		watchlist_lst = []
		self.sanitize_watchlist()
		for row in self.watchlist.get():
			watchlist_lst.append(row['symbol'])

		try:
			self.stream(watchlist_lst)
		except httplib.IncompleteRead:
			self.logger.error('Exception: ' + str(sys.exc_info()[0]) + '. Recursively calling Ticker.start')
			self.handle_stream_exception()
		except ssl.SSLError:
			clock = Clock()
			if clock.is_market_open():
				self.logger.error('Exception: ' + str(sys.exc_info()[0]) + '. Market still open. Recursively calling Ticker.start')
				self.handle_stream_exception()

			self.logger.error('Exception: ' + str(sys.exc_info()[0]) + '. Market closed. Exiting.')

	def handle_stream_exception(self):
		self.quotes.clear()
		self.trades.clear()
		self.start()

	def sanitize_watchlist(self):
		self.logger.info('sanitizing watchlist')
		
		watchlist_lst = []
		for row in self.watchlist.get():
			watchlist_lst.append(row['symbol'])
		
		quotes = self.tk.get_quotes(watchlist_lst)
		if quotes == None:
			for symbol in watchlist_lst:
				self.watchlist.remove(symbol)

			return

		for symbol in watchlist_lst:
			has_symbol = False
			for quote in quotes:
				if symbol == quote['symbol']:
					has_symbol = True

			if not has_symbol:
				self.watchlist.remove(symbol)