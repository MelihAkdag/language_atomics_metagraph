#!/usr/bin/python
# Filename: Conception.py
# Description: Implementation of the Conception class

from cor.knowledge.Concept import Concept
from cor.metagraph.MetaGraph import MetaGraph, Vertex, Arc
from core.utilities.Errors import ErrorCode

class PrintCtxt:
	def __init__(self):
		self.lines	= []
		self.indent	= 0
		return
	

class Conception(MetaGraph):
	def __init__(self):
		MetaGraph.__init__(self)
		self.root	= None
		return	


	def union(self, other_knowledge):
		pass

	def intersection(self, other_knowledge):
		pass

	def difference(self, other_knowledge):
		pass

	def symmetric_difference(self, other_knowledge):
		pass

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
				

	def __str__(self):
		ctxt	= PrintCtxt()
		self.root.dfs( 
				Conception.__print_node, 
				ctxt, 
				True,
				1024, 
				Conception.__print_preprocess,
				Conception.__print_postprocess )
		
		return '\n'.join(ctxt.lines)
	
	@staticmethod
	def __print_preprocess(node:Concept, ctxt:PrintCtxt, level:int):
		ctxt.indent	+= 1
		return ErrorCode.ERROR_CONTINUE

	@staticmethod
	def __print_postprocess(node:Concept, ctxt:PrintCtxt, level:int):
		ctxt.indent	-= 1
		return ErrorCode.ERROR_CONTINUE

	@staticmethod
	def __print_node(node:Concept, ctxt:PrintCtxt, level:int):
		ctxt.lines.append( f'{" " * ctxt.indent} {ctxt.indent}-Node: {node.name} (id={node.id})' )
		return ErrorCode.ERROR_CONTINUE


if __name__ == "__main__":
	test = Conception()

