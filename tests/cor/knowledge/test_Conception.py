#!/usr/bin/python
# Filename: test_ConceptCloud.py
# Description: Test cases for the ConceptCloud class

from cor.knowledge.Conception import Conception
from cor.knowledge.Concept import Concept
from cor.knowledge.Knowledge import Knowledge

import unittest


class ConceptCloudTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		return
		
	@classmethod
	def tearDownClass(self):
		return
		
	def setUp(self):
		self.lhs	= Conception()
		self.rhs	= Conception()

		self.lhs.load({
			'A': ['B','C'],
			'B': ['D','C'],
			'C': ['D'],
			'D': [],
			})

		self.rhs.load({
			'A': ['B'],
			'B': ['E','F'],
			'E': ['F'],
			'F': ['B','E'],
			})

		return
		
	def tearDown(self):
		return
		
	def test_union(self):
		u = self.lhs.union( self.rhs )
		print(f'Union({len(u.vertices)}):{u}')
		return

	def test_intersection(self):
		u = self.lhs.intersection( self.rhs )
		print(f'Intersection({len(u.vertices)}):{u}')
		return

	def test_difference(self):
		u = self.lhs.difference( self.rhs )
		print(f'Difference({len(u.vertices)}):{u}')
		return

	def test_symmetric_difference(self):
		u = self.lhs.symmetric_difference( self.rhs )
		print(f'Symmetric Difference({len(u.vertices)}):{u}')
		return

if __name__ == '__main__':
    unittest.main()
