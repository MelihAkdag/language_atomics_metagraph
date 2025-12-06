#!/usr/bin/python
# Filename: MetaGraphDatabase.py
# Description: Active record design pattern for graph database access

from core.utilities.MultiTableActiveObject import MultiTableActiveObject
from core.utilities.ActiveRecord import ActiveRecord
import core.utilities.GraphDatabase as GraphDatabase

class MetaGraphDatabaseConnection(GraphDatabase.GraphDatabaseConnection):
	def __init__(self, dbpath):
		GraphDatabase.GraphDatabaseConnection.__init__(self, dbpath)
		return

class Arc(GraphDatabase.Arc):
	def __init__(self, rec, arc_id):
		GraphDatabase.Arc.__init__(self, rec, arc_id)
		return
		
	def is_property(self, field):
		return field not in ['id','guid','graph_id','name','clsid','objid','type','weight','start','end', 'anchor']

	def get_anchor(self):
		return self.rec.get(self.id, 'anchor')

	def set_anchor(self, value):
		return self.rec.set(self.id, 'anchor', value)
			
	@property
	def anchor(self):
		return self.get_anchor()
	
class MetaGraphDatabase(GraphDatabase.GraphDatabase):
	def __init__(self, dbpath:str, graph_id=-1):
		GraphDatabase.GraphDatabase.__init__(self,
				dbpath, 
				graph_id, 
				MetaGraphDatabaseConnection(dbpath)
				)
		return

	def create_arc(self, rec, arc_id):
		return Arc( rec, arc_id )

		
if __name__ == '__main__':
	test = MetaGraphDatabase( "graph.s3db", 14 )
