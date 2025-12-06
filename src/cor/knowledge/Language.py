#!/usr/bin/python
# Filename: Language.py
# Description: Implementation of the Language class

from cor.metagraph.MetaGraphDatabase import MetaGraphDatabase
from cor.knowledge.Concept import Concept

from enum import Enum
from typing import Any

class Atomic(Enum):
	OF		= 1
	HAS		= 2
	IS_A	= 3
	IN		= 4
	FROM	= 5
	TO		= 6
	RELATES	= 7
	CONTAINS= 8
	IS		= 9
	


class Language:
	def __init__(self, graph:MetaGraphDatabase):
		self.graph = graph
		return

	def OF(self, a, A, B):
		#   Atomic.OF <-> ~ATOMIC.HAS
		self.link(A, B, Atomic.HAS, a)
		return

	def HAS(self, A, a, B):
		self.link(A, B, Atomic.HAS, a)
		return

	def IS_A(self, B, A):
		self.link(B, A, Atomic.IS_A)
		return
	
	def IN(self, A, B):
		#   Atomic.IS_A <-> ~ATOMIC.IN
		self.link(B, A, Atomic.IS_A)
		return
	
	def FROM(self, A, B, P):
		link 	= self.link(A, B, Atomic.FROM)
		link['program'] = P
		return

	def TO(self, B, A, P):
		link 	= self.link(B, A, Atomic.TO)
		link['program'] = P
		return

	def RELATES(self, A, B, c, by):
		link 	= self.link(A, B, Atomic.RELATES)
		return

	def OF(self, B, A):
		self.link(B, A, Atomic.OF)
		return
	
	def CONTAINS(self, A, B):
		self.link(A, B, Atomic.CONTAINS)
		return

	def IS(self, A, B):
		self.link(A, B, Atomic.IS)
		return

	def link(self, a:Any, b:Any, relation:Atomic, metadata:Any=None):
		a_node	= self.get_node(a)
		b_node	= self.get_node(b)

		ln_name	= relation.name if metadata is None else f'{relation.name}.{metadata}'
		edge 	= self.graph.join(a_node.id, b_node.id, relation.value, None, ln_name)

		if metadata is not None:
			edge['anchor'] = self.get_node(metadata).id
		
		return edge


	def get_node(self, name):
		v = self.graph.get_vertex_by_name(name, auto_add=False)
		if v is None:
			v = self.graph.add_vertex(name, Concept.to_id(name))
		
		return v

if __name__ == "__main__":
	test = Language()

