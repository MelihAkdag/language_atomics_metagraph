#!/usr/bin/python
# Filename: test_ConceptCloud.py
# Description: Test cases for the ConceptCloud class

from cor.knowledge.Conception import Conception
from cor.knowledge.Concept import Concept
from cor.knowledge.Knowledge import Knowledge
from core.utilities.Errors import ErrorCode

import unittest

def print_node(node:Concept, ctxt, level:int):
	level	 = 1024-level
	print( f'{" " * level} Node: {node.name} (id={node.id})' )
	return ErrorCode.ERROR_CONTINUE

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
		c = Conception()
		c.load('Melih', self.kb, depth=2)

		print( f'vertices = {len(c.vertices)}' )

		c.root.dfs( print_node, None, True )
		return

if __name__ == '__main__':
    unittest.main()
