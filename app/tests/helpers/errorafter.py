class ErrorAfter:
	def __init__(self, limit):
		self.limit = limit
		self.calls = 0

	def __call__(self):
		self.calls += 1
		if self.calls > self.limit:
			raise Exception('limit reached')