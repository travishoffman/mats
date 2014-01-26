class Analyst:
	def __init__(self, conn):
		self.conn = conn

	def start(self):
		self.conn.send(json.dumps({'type': 'signal', 'data': 'hold'}))