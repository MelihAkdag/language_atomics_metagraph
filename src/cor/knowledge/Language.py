#!/usr/bin/python
# Filename: Language.py
# Description: Implementation of the Language class

from cor.metagraph.MetaGraphDatabase import MetaGraphDatabase
from enum import Enum, Flag
from typing import Any

class ZoneStatus(Enum):
	OF		= 1
	HAS		= 2
	IS_A	= 3
	IN		= 4
	FROM	= 5
	TO		= 6
	RELATES	= 7
	CONTAINS= 8
	


class Language:
	def __init__(self, graph):
		self.graph = graph
		return

	def OF(self, a, A):
		pass

	def HAS(self, A, a):
		pass

	def IS_A(self, B, A):
		pass
	
	def IN(self, A, B):
		pass

	def FROM(self, A, B, P):
		pass

	def TO(self, B, A, P):
		pass

	def RELATES(self, A, B, c, by):
		pass

	def OF(self, B, A):
		pass

	def CONTAINS(self, A, B):
		pass

	def IS(self, A, B):
		pass
		

if __name__ == "__main__":
	test = Language()

