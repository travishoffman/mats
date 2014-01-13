from pymongo import MongoClient

class DbLayer:
	def __init__(self):
		self.client = MongoClient('localhost', 27017)
		self.db = self.client.mats