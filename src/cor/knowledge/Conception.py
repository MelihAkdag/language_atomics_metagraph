#!/usr/bin/python
# Filename: Conception.py
# Description: Implementation of the Conception class

from cor.metagraph.MetaGraph import MetaGraph, Vertex, Arc
from cor.knowledge.Knowledge import Knowledge
from cor.knowledge.Concept import Concept

class Conception(MetaGraph):
	def __init__(self):
		MetaGraph.__init__(self)
		self.root	= None
		return	

	def load(self, name:str, kb:Knowledge, depth=3):
		# find root concept
		v = kb[name]
		if v is None:
			raise ValueError(f'Concept {name} not found in knowledge base.')

		links 		= {}
		self.root 	= self.__traverse_subgraph(v, kb, depth, links)

		self.__link_nodes(links, kb)
		return

	def __link_nodes(self, links, kb:Knowledge):
		for start, arcs in links.items():
			for aid in arcs:
				a 		= kb.graph.get_arc(aid)
				
				self.join(
					start, 
					a['end'], 
					a['weight'], 
					a['name'], 
					a.anchor,
					a.id)
		return
	
	def __traverse_subgraph(self, v, kb:Knowledge, depth:int, links):
		c = Concept.clone(v)
		if depth < 0:
			return c

		# If the concept already exists in the conception, return it
		if self.add(c) is False:
			return c
		
		# Clone the arcs
		arcs 		= kb.graph.get_arcs_for_vertex( v.id )
		links[v.id] = arcs

		for aid in arcs:
			a 		= kb.graph.get_arc(aid)
			anchor 	= self.__create_node(a['anchor'], kb, depth - 1, links)
			start  	= self.__create_node(a['start'], kb, depth - 1, links)
			end    	= self.__create_node(a['end'], kb, depth - 1, links)

		return c

	def __create_node(self, v, kb:Knowledge, depth:int, links):
			if v == 0:
				return None
			
			return self.__traverse_subgraph(
				kb.graph.get_vertex(v), 
				kb, 
				depth,
				links)
				

	def __str__(self):
		return 
	@property
	def name(self):
		if self.root is None:
			return None
		return self.root.name
	
	@property
	def weight(self):
		if self.root is None:
			return None
		return self.root.weight

if __name__ == "__main__":
	test = Conception()

