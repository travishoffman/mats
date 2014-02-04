from watchlist import WatchList
from quote import Quote
from trade import Trade
from tradeking import TradeKing
from clock import Clock
from event import TradeEvent, QuoteEvent, StatusEvent, Event
import os
import logging
import httplib
import ssl
import json

class Ticker:
	def __init__(self, conn):
		self.logger = logging.getLogger('mats')
		self.clock = Clock()
		self.conn = conn
		self.watchlist = WatchList()
		self.quotes = {}
		self.trades = {}

		try:
			config_f = open('config.json', 'r')
			conf = json.load(config_f)['tradeking']
			config_f.close()
		except:
			self.logger.error('ticker: config.json is not properly configured')

		self.tk = TradeKing({
			'consumer_key': conf['consumer_key'],
			'consumer_secret': conf['consumer_secret'],
			'oauth_token': conf['oauth_token'],
			'oauth_token_secret': conf['oauth_token_secret']
		})
		self.handlers = {
			'status': self.status_handler,
			'quote': self.quote_handler,
			'trade': self.trade_handler
		}

	def status_handler(self, resp):
		if resp['status'] == 'connected':
			self.conn.send(StatusEvent(name='connected'))

	def quote_handler(self, resp):
		symbol = resp['quote']['symbol']
		if resp['quote']['symbol'] not in self.quotes.keys():
			q = Quote(resp['quote'])
		else:
			q = Quote(self.quotes[symbol].merge(resp['quote']))

		if q.is_complete() is False:
			quote_data = self.tk.get_quotes([symbol])
			q.merge(quote_data)

		oid = q.save()
		self.quotes[symbol] = q
		self.conn.send(QuoteEvent(name='new_quote', object_id=oid, symbol=symbol))

	def trade_handler(self, resp):
		symbol = resp['trade']['symbol']
		if resp['trade']['symbol'] not in self.trades.keys():
			t = Trade(resp['trade'])
		else:
			t = Trade(self.trades[symbol].merge(resp['trade']))

		if t.is_complete() is False:
			trade_data = self.tk.get_quotes([symbol])
			t.merge(trade_data)

		oid = t.save()
		self.trades[symbol] = t
		self.conn.send(TradeEvent(name='new_trade', object_id=oid, symbol=symbol))

	def stream(self, watchlist_lst):
		for resp in self.tk.get_stream(watchlist_lst):
			self.handlers[resp.keys()[0]](resp)

	def start(self):
		watchlist_lst = []
		self.sanitize_watchlist()
		for row in self.watchlist.get():
			watchlist_lst.append(row['symbol'])

		if len(watchlist_lst) == 0:
			self.logger.info('ticker: watchlist is empty. exiting.')
			self.conn.send(Event(name='empty_watchlist'))
			return

		try:
			self.stream(watchlist_lst)
		except httplib.IncompleteRead:
			self.conn.send(Event(name='incomplete_read'))
		except ssl.SSLError:
			self.conn.send(Event(name='ssl_error'))

	def sanitize_watchlist(self):
		self.logger.info('ticker: sanitizing watchlist')
		
		watchlist_lst = []
		for row in self.watchlist.get():
			watchlist_lst.append(row['symbol'])
		
		if len(watchlist_lst) == 0:
			return 

		quotes = self.tk.get_quotes(watchlist_lst)
		if quotes == None:
			for symbol in watchlist_lst:
				self.watchlist.remove(symbol)

			return
		elif type(quotes) is dict:
			quotes = [quotes]

		for symbol in watchlist_lst:
			has_symbol = False
			for quote in quotes:
				if symbol == quote['symbol']:
					has_symbol = True

			if not has_symbol:
				self.watchlist.remove(symbol)