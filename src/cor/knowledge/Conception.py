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
	def __init__(self, name:None, kb=None, depth=3):
		MetaGraph.__init__(self)
		self.root	= None

		# Load the conception from knowledge base
		if name is not None and kb is not None:
			kb.load( self, name, depth )
				
		return	

	def clone(self):
		return self.copy_to( Conception() )

	def union(self, rhs:MetaGraph):
		return self.clone().union_update( rhs )

	def intersection(self, rhs:MetaGraph):
		return self.clone().intersection_update( rhs )

	def difference(self, rhs:MetaGraph):
		return self.clone().difference_update( rhs )

	def symmetric_difference(self, rhs:MetaGraph):
		return self.clone().symmetric_difference_update( rhs )
	
	def union_update(self, rhs:MetaGraph):
		rhs.copy_to( self )
		return self

	def intersection_update(self, rhs:MetaGraph):
		rhsset	= rhs.to_set()
		lhsset	= self.to_set()
		result	= lhsset.intersection( rhsset )
		return self.filter(result)

	def difference_update(self, rhs):
		rhsset	= rhs.to_set()
		lhsset	= self.to_set()
		result	= lhsset.difference( rhsset )
		return self.filter(result)

	def symmetric_difference_update(self, rhs):
		rhsset	= rhs.to_set()
		lhsset	= self.to_set()
		result	= lhsset.symmetric_difference( rhsset )
		return self.filter(result)


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

