#!/usr/bin/python
# Filename: Knowledge.py
# Description: Implementation of the Knowledge class

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

	def union(self, other_knowledge):
		pass

	def intersection(self, other_knowledge):
		pass

	def difference(self, other_knowledge):
		pass

	def symmetric_difference(self, other_knowledge):
		pass

	def __getitem__(self, name):
		v = self.graph.get_vertex_by_name(name, auto_add=False)
		if v is None:
			v = self.graph.add_vertex(name, Concept.to_id(name))

		return v
		
if __name__ == "__main__":
	test = Knowledge()

