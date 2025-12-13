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
	def __init__(self, name=None, kb=None, depth=3):
		MetaGraph.__init__(self)
		self.root	= None

		# Load the conception from knowledge base
		if name is not None and kb is not None:
			kb.load( self, name, depth )
				
		return	

	def remove(self, vertex):
		if self.root is not None and vertex.id == self.root.id:
			MetaGraph.remove(self, vertex)
			self.root = list(self.vertices.values())[0] if len(self.vertices) > 0 else None
		else:
			MetaGraph.remove(self, vertex)

	def new_vertex(self, id=-1, weight=1.0, name="", guid=None):
		return Concept(name, id, weight,  guid)

	def load(self, info):
		for k in info.keys():
			c 	= Concept(k)
			if self.root is None:
				self.root = c

			self.add( c )

	
		for k, v in info.items():
			for e in v:
				self.join( k, e )
		return self
	
	def clone(self):
		copy = Conception()
		v	= self.root
		if v is not None:
			copy.root = self.new_vertex(v.id, v.weight, v.name, v.guid)
			copy.add( copy.root )
		
		self.copy_to( copy )
	
		if v is not None:
			for a in v.arcs:
				copy.join( a.start.name, a.end.name, a.weight, a.name, a.anchor, a.guid, a.id )

		return copy		


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

		# Need top copy to incorporate all vertices and arcs from 'rhset'
		rhs.copy_to( self )
		return self.filter(result)

	def __add__(self, rhs):
		return self.union( rhs )
	
	def __sub__(self, rhs):
		return self.difference( rhs )
	
	def __mod__(self, rhs):
		return self.symmetric_difference( rhs )
	
	def __truediv__(self, rhs):
		return self.intersection( rhs )

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

