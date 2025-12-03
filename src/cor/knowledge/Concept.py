#!/usr/bin/python
# Filename: Concept.py
# Description: Implementation of the Concept class

import hashlib

class Concept:
	def __init__(self, name, node):
		self.name		= name
		self.node		= node
		self._id		= None
		return


	def OF(self):
		pass

	def HAS(self):
		pass

	def IS_A(self):
		pass
	
	def IN(self):
		pass

	def FROM(self):
		pass

	def TO(self):
		pass

	def RELATES(self):
		pass

	def OF(self):
		pass

	def CONTAINS(self):
		pass

	def IS(self, other):
		pass

	@property
	def id(self):
		if self._id is None:
			self._id	= Concept.to_id(self.name)

		return self._id


	def __str__(self):
		return self.name

	@staticmethod
	def to_id(name):
		return int.from_bytes(hashlib.sha256(name.encode('utf-8')).digest()[:4])
		
if __name__ == "__main__":
	test = Concept('xxx')
	print(test)
	print(test.id)

