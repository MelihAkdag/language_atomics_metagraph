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
		self.kb = Knowledge('graph')
		return
		
	def tearDown(self):
		return
		
	def test_load(self):
		c = self.kb.slice('Melih', depth=2)

		print( f'vertices = {len(c.vertices)}' )
		print( c )
		return

if __name__ == '__main__':
    unittest.main()
