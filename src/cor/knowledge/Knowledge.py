#!/usr/bin/python
# Filename: Knowledge.py
# Description: Implementation of the Knowledge class

from cor.knowledge.Conception import Conception
from cor.knowledge.Concept import Concept
from cor.knowledge.Language import Language
from cor.metagraph.MetaGraphDatabase import MetaGraphDatabase

import os, shutil

class Knowledge:
	def __init__(self, name, template=None):
		self.__create_database(name, template)
		self.language	= None
		return

	def __create_database(self, name, template):
		path =	f'{name}.s3db'
		if os.path.exists(path):
			self.graph	= MetaGraphDatabase(path)
			self.graph.create(name,1)
			return
		
		if template is None:
			raise FileNotFoundError(f'Database file {path} does not exist.')
		
		shutil.copy(template, path)
		
		self.graph	= MetaGraphDatabase(path)
		self.graph.create(name,1)
		return
	
	def speak(self):
		if self.language is None:
			self.language = Language(self.graph)

		return self.language

	def slice(self, name:str, depth:int):
		concept = Conception()
		self.load(concept, name, depth)
		return concept

	def get_all(self):
		concept = Conception()
		conn 	= self.graph.conn.connect()
		t   	= (self.graph.id,)

		# Get vertices
		c		= conn.cursor()
		c.execute('SELECT id, name, value, guid, clsid, objid FROM vertices WHERE graph_id=?', t)
		for row in c:
			v = Concept( row[1], row[0], row[2], row[3] )
			concept.add( v )
			if concept.root is None:
				concept.root = v
		c.close()

		# Get arcs
		c		= conn.cursor()
		c.execute('SELECT id, name, weight, guid, start, end, anchor FROM arcs WHERE graph_id=?', t)
		for row in c:
			a = concept.join( row[4], row[5], row[2], row[6], row[0] )
		c.close()

		return concept
	
	def __getitem__(self, name):
		v = self.graph.get_vertex_by_name(name, auto_add=False)
		if v is None:
			v = self.graph.add_vertex(name, Concept.to_id(name))

		return v


	def load(self, concept, name:str, depth=3):
		# find root concept
		v = self[name]
		if v is None:
			raise ValueError(f'Concept {name} not found in knowledge base.')

		links 			= {}
		concept.root 	= self.__traverse_subgraph( concept, v, depth, links)

		self.__link_nodes(concept, links)
		return

	def __link_nodes(self, concept, links):
		for start, arcs in links.items():
			for aid in arcs:
				a 		= self.graph.get_arc(aid)
				
				concept.join(
					start, 
					a['end'], 
					a['weight'], 
					a['name'], 
					a.anchor,
					a.id)
		return

	def __traverse_subgraph(self, concept, v, depth:int, links):
		c = Concept.clone(v)
		if depth < 0:
			return c

		# If the concept already exists in the conception, return it
		if concept.add(c) is False:
			return c
		
		# Clone the arcs
		arcs 		= self.graph.get_arcs_for_vertex( v.id )
		links[v.id] = arcs

		for aid in arcs:
			a 		= self.graph.get_arc(aid)
			anchor 	= self.__create_node(concept, a['anchor'], depth - 1, links)
			start  	= self.__create_node(concept, a['start'], depth - 1, links)
			end    	= self.__create_node(concept, a['end'], depth - 1, links)

		return c

	def __create_node(self, concept, v, depth:int, links):
			if v == 0:
				return None
			
			return self.__traverse_subgraph(
				concept,
				self.graph.get_vertex(v), 
				depth,
				links )

if __name__ == "__main__":
	test = Knowledge()

