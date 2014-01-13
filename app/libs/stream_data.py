from dblayer import DbLayer
import copy

class StreamData(DbLayer):
	def __init__(self, fields, data):
		DbLayer.__init__(self)
		self._fields = fields
		self._data = self._weed(data)

	def is_complete(self):
		for field in self._fields:
			if field not in self._data.keys():
				return False

		return True

	def _weed(self, data):
		for field in data.keys():
			if field not in self._fields:
				del data[field]

		return data

	def merge(self, data):
		new_data = copy.deepcopy(self._data)
		for field in data.keys():
			if field in self._fields:
				new_data[field] = data[field]

		return new_data