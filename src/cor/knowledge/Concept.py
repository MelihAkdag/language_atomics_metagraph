#!/usr/bin/python
# Filename: Concept.py
# Description: Implementation of the Concept class

from cor.metagraph.MetaGraph import Vertex

import hashlib

class Concept(Vertex):
	def __init__(self, v=None):
		self.id		= v.id
		self.name	= v['name']
		self.guid	= v['guid']
		self.value	= v['value']
		self.arcs	= []
		self.anchor	= None
		return

	@staticmethod
	def clone(v):
		return Concept(v)

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
	
	def __str__(self):
		return self.name

	@staticmethod
	def to_id(name):
		return int.from_bytes(hashlib.sha256(name.encode('utf-8')).digest()[:4])
		
if __name__ == "__main__":
	test = Concept('xxx')
	print(test)
	print(test.id)

