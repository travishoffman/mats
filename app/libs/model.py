from pymongo import MongoClient

class Model:
	def __init__(self, conf):
		self.client = MongoClient(conf['host'], conf['port'])

	def save(self):
		