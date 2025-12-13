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
		self.anchor		= None
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

	def bfs( self, fn, ctxt, visitanchor=False, depth=1024, preproc=None, postproc=None ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			visitanchor -- Whether to visit anchor nodes
			depth=1024 -- Maximum depth to recurse into
			preproc -- Preprocessor callback
			postproc -- Postprocessor callback
		"""
		if depth <= 0:
			return ErrorCode.NOERROR
		
		visited = set()
		visited.add( self )

		result	= self.visit( fn, ctxt, visitanchor, visited, depth, preproc, postproc, False )
		
		if result == ErrorCode.NOERROR or result == ErrorCode.ERROR_CONTINUE:
			return self.traverse_bfs( fn, ctxt, depth-1, visitanchor, visited )
		
		return result

	def dfs( self, fn, ctxt, visitanchor=False, depth=1024, preproc=None, postproc=None ):
		""" function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			visitanchor -- Whether to visit anchor nodes
			depth=1024 -- Maximum depth to recurse into
			preproc -- Preprocessor callback
			postproc -- Postprocessor callback
		"""
		if depth <= 0:
			return ErrorCode.NOERROR
		
		visited = set()
		visited.add( self )

		result	= self.visit( fn, ctxt, visitanchor, visited, depth, preproc, postproc, True )
		
		if result == ErrorCode.NOERROR or result == ErrorCode.ERROR_CONTINUE:
			return self.traverse_dfs( fn, ctxt, depth-1, visitanchor, visited, preproc, postproc )
		
		return result
	

	def traverse_dfs( self, fn, ctxt, maxlevel, visitanchor, visited, preproc, postproc ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			maxlevel=1024 -- Maximum depth to recurse into
			preproc -- Preprocessor callback
			postproc -- Postprocessor callback
		"""

		result = ErrorCode.NOERROR
		if maxlevel <= 0:
			return result

		# Traverse current level
		for a in self.arcs:
			if a.end in visited:
				continue

			visited.add( a.end )

			if preproc is not None:
				result	= preproc( a.end, ctxt, maxlevel )

				if result == ErrorCode.ERROR_NO_MORE_ITEMS:
					return ErrorCode.ERROR_CONTINUE

				if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
					return result
				
			result	= a.end.visit( fn, ctxt, visitanchor, visited, maxlevel, preproc, postproc, True )

			if result == ErrorCode.ERROR_NO_MORE_ITEMS:
				return ErrorCode.ERROR_CONTINUE
			
			if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
				return result
			
			result 	= a.end.traverse_dfs( fn, ctxt , maxlevel-1, visitanchor, visited, preproc, postproc )
			if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
				return result

			if postproc is not None:
				result	= postproc( a.end, ctxt, maxlevel )
				
				if result == ErrorCode.ERROR_NO_MORE_ITEMS:
					return ErrorCode.ERROR_CONTINUE
				
				if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
					return result

		return result

	def traverse_bfs( self, fn, ctxt, maxlevel, visitanchor, visited, preproc, postproc ):
		""" Helper function to iterate through vertices of a graph and invoke a callback
		Arguments
			fn -- Function to call back
			ctxt -- Context argument passed to the function
			maxlevel=1024 -- Maximum depth to recurse into
			preproc -- Preprocessor callback
			postproc -- Postprocessor callback
		"""

		result = ErrorCode.NOERROR
		if maxlevel <= 0:
			return result

		# Traverse current level
		for a in self.arcs:
			if a.end in visited:
				continue

			visited.add( a.end )

			if preproc is not None:
				result	= preproc( a.end, ctxt, maxlevel )
				
				if result == ErrorCode.ERROR_NO_MORE_ITEMS:
					return ErrorCode.ERROR_CONTINUE
				
				if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
					return result
				
			result	= a.end.visit( fn, ctxt, visitanchor, visited, maxlevel, preproc, postproc, False )
			
			if result == ErrorCode.ERROR_NO_MORE_ITEMS:
				return ErrorCode.ERROR_CONTINUE
			
			if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
				return result

			if postproc is not None:
				result	= postproc( a.end, ctxt, maxlevel )
				
				if result == ErrorCode.ERROR_NO_MORE_ITEMS:
					return ErrorCode.ERROR_CONTINUE
				
				if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
					return result

		if maxlevel <= 1:
			return result
		
		# Recurse into next level
		for a in self.arcs:
			if a.end in visited:
				continue

			result 	= a.end.traverse_bfs( fn, ctxt , maxlevel-1, visitanchor, visited, preproc, postproc )
			if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
				return result
			
		return result

	def visit(self, fn, ctxt, visitanchor, visited, maxlevel, preproc, postproc, isdfs=True ):
		visited.add( self )
		result	= fn( self, ctxt, maxlevel )

		if result == ErrorCode.ERROR_NO_MORE_ITEMS:
			return ErrorCode.ERROR_CONTINUE
		

		if visitanchor == False or self.anchor is None:
			return result
		
		if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
			return result

		# Visit the anchor node		
		visited.add( self.anchor )

		if preproc is not None:
			result	= preproc( self.anchor, ctxt, maxlevel )
			
			if result == ErrorCode.ERROR_NO_MORE_ITEMS:
				return ErrorCode.ERROR_CONTINUE
			
			if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
				return result

		result	= fn( self.anchor, ctxt, maxlevel )
		
		if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE, ErrorCode.ERROR_NO_MORE_ITEMS]:
			return result

		if postproc is not None:
			result	= postproc( self.anchor, ctxt, maxlevel )
			
			if result == ErrorCode.ERROR_NO_MORE_ITEMS:
				return ErrorCode.ERROR_CONTINUE
			
			if result not in [ErrorCode.NOERROR, ErrorCode.ERROR_CONTINUE]:
				return result

		if isdfs:
			return self.anchor.traverse_dfs( fn, ctxt , maxlevel, visitanchor, visited, preproc, postproc )
		else:
			return self.anchor.traverse_bfs( fn, ctxt , maxlevel, visitanchor, visited, preproc, postproc )

	@property
	def num_arcs(self):			
		return len(self.arcs)

	
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
			if v.id == vertex.id:
				continue
			
			for a in list(v.arcs):
				if (a.end.id == vertex.id) or (a.start.id == vertex.id):
					v.arcs.remove( a )
	
		del self.vertices[vertex.name]
		return

	def filter(self, matches:set):
		remove_list = []
		for v in self.vertices.values():
			if v.id not in matches:
				remove_list.append( v )
		
		for v in remove_list:
			self.remove( v )
		return self

	def clone(self):
		return self.copy_to( MetaGraph() )

	def copy_to(self, copy):		
		# Clone vertices
		for v in self.vertices.values():
			copy.add( self.new_vertex(v.id, v.weight, v.name, v.guid) )
		
		# Clone arcs
		for v in self.vertices.values():
			for a in v.arcs:
				copy.join( a.start.name, a.end.name, a.weight, a.name, a.anchor, a.guid, a.id )
		
		return copy

	def new_vertex(self, id=-1, weight=1.0, name="", guid=None):
		return Vertex(id, weight, name, guid)
	
	def to_set(self):
		result = set()
		for v in self.vertices.values():
			result.add( v.id )

		return result

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
			count += v.num_arcs
			
		return count

if __name__ == '__main__':
	test = MetaGraph( "graph" )
