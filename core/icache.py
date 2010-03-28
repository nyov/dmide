import libbyond.dmi as dmi
import thread

cache_level = 2
# 0 - do not cache
# 1 - cache for the duration of the operation, need to call clear after operation
# 2 - cache forever

class IconCache:
	def __init__(self):
		self.cache = {}

	def read(self, path, request=None):
		if not cache_level:
			return dmi.DMIREAD(path)

		if cache_level == 1:
			if request not in self.cache:
				self.cache[request] = {}

			if path not in self.cache[request]:
				self.cache[request][path] = dmi.DMIREAD(path)

			return self.cache[request][path]

		else:
			if path not in self.cache:
				self.cache[path] = dmi.DMIREAD(path)

			return self.cache[path]

	def clear(self, request=None):
		if request in self.cache:
			del self.cache[request]
		import gc
		gc.collect(2)

	def purge(self):
		self.cache = {}
