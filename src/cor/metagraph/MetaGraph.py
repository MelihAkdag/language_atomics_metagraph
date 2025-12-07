#!/usr/bin/python
# Filename: MetaGraph.py
# Description: Active record design pattern for graph database access

from core.utilities.Errors import ErrorCode

import uuid
from datetime import datetime

class Arc:
	def __init__(self, start, end, id=-1, weight=1.0, name="", anchor=None, guid=None):
		self.id			= id
		self.guid		= guid if guid is not None else uuid.uuid4()
		self.name		= name
		self.weight		= weight
		self.start		= start
		self.end		= end
		self.anchor		= anchor
		return
		

class Vertex:
	def __init__(self, id=-1, weight=1.0, name="", guid=None):
		self.id			= id
		self.guid		= guid if guid is not None else uuid.uuid4()
		self.name		= name
		self.weight		= weight
		self.arcs		= []
		return

	def connected(self, b):
		for arc in self.arcs:
			if arc.end == b:
				return True
			
		return False
	
	def detach(self, b):
		for arc in self.arcs:
			if arc.end == b:
				self.arcs.remove( arc )
				return True
			
		return False

	def for_each_vertex( self, fn, ctxt ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
		"""
		for a in self.arcs:
			result	= fn( a.end, ctxt )
			if result == ErrorCode.NOERROR:
				continue
			elif result == ErrorCode.ERROR_CONTINUE:
				continue
			else:
				return result

		return result

	def bfs( self, fn, ctxt, visitanchor=False, depth=1024 ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			visitanchor -- Whether to visit anchor nodes
			depth=1024 -- Maximum depth to recurse into
		"""
		if depth <= 0:
			return ErrorCode.NOERROR
		
		visited = set()
		visited.add( self )

		result	= self.visit( fn, ctxt, visitanchor, visited, depth )
		
		if result == ErrorCode.NOERROR or result == ErrorCode.ERROR_CONTINUE:
			return self.traverse_bfs( fn, ctxt, depth-1, visitanchor, visited )
		
		return result

	def dfs( self, fn, ctxt, visitanchor=False, depth=1024 ):
		""" function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			visitanchor -- Whether to visit anchor nodes
			depth=1024 -- Maximum depth to recurse into
		"""
		if depth <= 0:
			return ErrorCode.NOERROR
		
		visited = set()
		visited.add( self )

		result	= self.visit( fn, ctxt, visitanchor, visited, depth )
		
		if result == ErrorCode.NOERROR or result == ErrorCode.ERROR_CONTINUE:
			return self.traverse_dfs( fn, ctxt, depth-1, visitanchor, visited )
		
		return result
	

	def traverse_dfs( self, fn, ctxt, maxlevel, visitanchor, visited ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			maxlevel=1024 -- Maximum depth to recurse into
		"""

		result = ErrorCode.NOERROR
		if maxlevel <= 0:
			return result

		# Traverse current level
		for a in self.arcs:
			if a.end in visited:
				continue

			visited.add( a.end )

			result	= a.end.visit( fn, ctxt, visitanchor, visited, maxlevel )
			
			if result == ErrorCode.NOERROR or result == ErrorCode.ERROR_CONTINUE:
				result 	= a.end.traverse_dfs( fn, ctxt , maxlevel-1, visitanchor, visited )
				if result == ErrorCode.NOERROR:
					continue
				elif result == ErrorCode.ERROR_CONTINUE:
					continue
				else:
					return result
				
			else:
				return result

		return result

	def traverse_bfs( self, fn, ctxt, maxlevel, visitanchor, visited ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			maxlevel=1024 -- Maximum depth to recurse into
		"""

		result = ErrorCode.NOERROR
		if maxlevel <= 0:
			return result

		# Traverse current level
		for a in self.arcs:
			if a.end in visited:
				continue

			visited.add( a.end )

			result	= a.end.visit( fn, ctxt, visitanchor, visited, maxlevel )
			
			if result == ErrorCode.NOERROR:
				continue
			elif result == ErrorCode.ERROR_CONTINUE:
				continue
			else:
				return result

		if maxlevel <= 1:
			return result
		
		# Recurse into next level
		for a in self.arcs:
			if a.end in visited:
				continue

			result 	= a.end.traverse_bfs( fn, ctxt , maxlevel-1 )
			if result == ErrorCode.NOERROR:
				continue
			elif result == ErrorCode.ERROR_CONTINUE:
				continue
			else:
				return result

		return result

	def visit(self, fn, ctxt, visitanchor, visited, level):
		visited.add( self )
		result	= fn( self, ctxt, level )
		
		if result == ErrorCode.NOERROR or result == ErrorCode.ERROR_CONTINUE:
			if visitanchor and self.anchor is not None:
				visited.add( self.anchor )
				return self.anchor( fn, ctxt, visitanchor )
			
		return result		
	
class MetaGraph:
	def __init__(self):
		self.vertices	= {}
		return
	
	def add(self, vertex):
		if self.vertices.get(vertex.name, None) is not None:
			return False
		
		self.vertices[vertex.name] = vertex
		return True

	def remove(self, vertex):		
		for v in self.vertices.values():
			if v == vertex:
				continue
			
			for a in v.arcs:
				if a.end == vertex:
					v.arcs.remove( a )
					break
	
		del self.vertices[vertex.name]
		return

	def join(self, a, b, weight=1.0, name="", anchor=None, guid=None, aid=-1):
		a = self.get_vertex(a)
		if a is None:
			return None

		b = self.get_vertex(b)
		if b is None:
			return None


		arc = Arc(a, b, aid, weight, name, anchor, guid)
		a.arcs.append( arc )
		return arc

	def detach(self, a, b):
		v = self.vertices.get(a, None)
		if v is None:
			return False
		
		return v.detach(b)

	def connected(self, a, b):
		v = self.vertices.get(a, None)
		if v is None:
			return False
		
		return v.connected(b)
	
	def for_each_vertex( self, fn, ctxt ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
		"""

		result = ErrorCode.NOERROR

		for v in self.vertices.values():
			result	= fn( v, ctxt )
			if result == ErrorCode.NOERROR:
				continue
			elif result == ErrorCode.ERROR_CONTINUE:
				continue
			else:
				break

		return result
	

	def for_each_arcs( self, fn, ctxt ):
		""" Helper function to iterate through arcs of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
		"""

		result = ErrorCode.NOERROR

		for v in self.vertices.values():
			for a in v.arcs:
				result	= fn( a, ctxt )
				if result == ErrorCode.NOERROR:
					continue
				elif result == ErrorCode.ERROR_CONTINUE:
					continue
				else:
					return result

		return result

	def get_vertex(self, id):
		if isinstance(id, int):
			for v in self.vertices.values():
				if v.id == id:
					return v
			return None
		
		return self.vertices.get(id, None)
	
	def get_arc(self, start, end):
		v = self.vertices.get(start, None)
		if v is None:
			return None
		
		for arc in v.arcs:
			if arc.end == end:
				return arc
			
		return None
	
	def __getvalue__(self, name):
		return self.vertices.get(name, None)


	@property	
	def num_vertices(self):
		return len(self.vertices)
	
	@property
	def num_arcs(self):
		count = 0
		for v in self.vertices.values():
			count += len(v.arcs)
			
		return count

if __name__ == '__main__':
	test = MetaGraph( "graph" )
