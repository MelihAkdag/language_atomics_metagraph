#!/usr/bin/python
# Filename: test_MetaGraphDatabase.py
# Description: Test cases for the MetaGraphDatabase class

from cor.metagraph.MetaGraphDatabase import MetaGraphDatabase

import unittest

class MetaGraphDatabaseTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		return
		
	@classmethod
	def tearDownClass(self):
		return
		
	def setUp(self):
		self.db = MetaGraphDatabase('graph.s3db')
		self.db.create('Concepts',1)
		return
		
	def tearDown(self):
		return
		
	def test_open(self):
		a = self.db.get_vertex_by_name('a')
		b = self.db.get_vertex_by_name('b')
		c = self.db.get_vertex_by_name('c')

		self.db.join( a, b )
		self.db.join( a, c )
		return


if __name__ == '__main__':
    unittest.main()
