from rauth.session import OAuth1Session
import httplib
import json
import logging

class TradeKing:
	def __init__(self, conf):
		self.logger = logging.getLogger('mats')
		self.sess = OAuth1Session(
			consumer_key=conf['consumer_key'],
			consumer_secret=conf['consumer_secret'],
			access_token=conf['oauth_token'],
			access_token_secret=conf['oauth_token_secret'])

		self.quote_ep = 'https://api.tradeking.com/v1/market/ext/quotes.json'
		self.clock_ep = 'https://api.tradeking.com/v1/market/clock.json'
		self.stream_ep = 'https://stream.tradeking.com/v1/market/quotes.json'

	def get_clock(self):
		resp = self.sess.get(self.clock_ep)
		return json.loads(resp.text)['response']['status']

	def get_quotes(self, symbols):
		symbols_str = ','.join(symbols)
		resp = self.sess.get(self.quote_ep,	params={'symbols': symbols_str})
		resp_obj = json.loads(resp.text)
		
		if not resp_obj['response']['quotes']:
			return None

		if type(resp_obj['response']['quotes']['quote']) is dict:
			return [resp_obj['response']['quotes']['quote']]

		return  resp_obj['response']['quotes']['quote']

	def get_stream(self, symbols):
		symbols_str = ','.join(symbols)
		resp = self.sess.get(self.stream_ep, params={'symbols': symbols_str},
			stream=True)

		json_str = ''
		for char in resp.iter_content():
			if char:
				json_str += char
				try:
					data = json.loads(json_str)
					json_str = ''
					yield data
				except:
					pass