class Event:
	def __init__(self, name):
		self.name = name

class TradeEvent(Event):
	def __init__(self, name, object_id, symbol):
		Event.__init__(self, name)
		self.object_id = object_id
		self.symbol = symbol

class QuoteEvent(Event):
	def __init__(self, name, object_id, symbol):
		Event.__init__(self, name)
		self.object_id = object_id
		self.symbol = symbol

class StatusEvent(Event):
	def __init__(self, name):
		Event.__init__(self, name)