#!/usr/bin/python
# Filename: test_Patterns.py
# Description: Test cases for the Patterns class

from core.utilities.Patterns import ChainOfResponsibility, Action

import unittest

class Ctxt:
	def __init__(self, value):
		self.value	= value
		return

	
class Command(Action):
	def __init__(self, name, increment=10):
		super().__init__()
		self.name	= name
		self.inc	= increment
		return
	
	def execute(self, ctxt):
		print(f'{self.name}:{ctxt.value}')
		ctxt.value	+= self.inc
		return ctxt.value

class SplitCtxt:
	def __init__(self, path, result, error):
		self.path		= path
		self.result		= result
		self.error		= error
		self.feedback	= None
		return

class Split(Command):
	def __init__(self, name, increment=10):
		super().__init__(name, increment)
		self.paths	= []
		return
	
	def split(self, cmd):
		path 		= ChainOfResponsibility(cmd)
		self.paths.append( SplitCtxt(path, 0, 0) )
		return path

	def execute(self, ctxt):
		result	= super().execute(ctxt)
		for p in self.paths:
			try:
				if p.feedback is not None:
					ctxt.value	+= p.feedback

				p.result 	= p.path.run(ctxt)
				p.error		= None
			except Exception as e:
				p.error		= e

		return result 
	
class PatternsTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		return
		
	@classmethod
	def tearDownClass(self):
		return
		
	def setUp(self):
		return
		
	def tearDown(self):
		return
		
	def test_chain_of_responsibility1(self):
		pipeline = ChainOfResponsibility.generate([
			Command('first1'),
			Command('second1'),
			Command('third1')
		])

		pipeline.run(Ctxt(200))
		return

	def test_chain_of_responsibility2(self):
		pipeline = ChainOfResponsibility()

		next	= pipeline.append(Command('first2'))
		next	= next.append( Command('second2'))
		next	= next.append( Command('third2'))

		pipeline.run(Ctxt(200))
		return

	

if __name__ == '__main__':
    unittest.main()
