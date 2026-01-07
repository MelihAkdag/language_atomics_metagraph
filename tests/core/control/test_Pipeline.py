#!/usr/bin/python
# Filename: Pipeline_test.py
# Description: Test cases for the Pipeline class

from core.control.Pipeline import *

import unittest, random

def P(x):
	return 2*x+1
	
def I(x):
	return x**2+x

def D(x):
	return 2

class ErrorFn:
	def __init__(self, value):
		self.value	= value
		return

	def __call__(self, *args, **kwds):
		expected	= P(self.value)+I(self.value)+D(self.value)
		return expected-args[0]

class PipelineTestCase(unittest.TestCase):
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
		
	def test_PID(self):
		self.pid_test()

	def pid_test(self):
		pipeline = Pipeline()

		next	= pipeline.append(Command('start'))
		next	= next.append( Split('split'))

		input	= 300
		err		= ErrorFn(input)

		with next as split:
			""" Mock PID controller """
			split.action.split(FunctionCommand('P', P))	
			split.action.split(FunctionCommand('I', I))
			split.action.split(FunctionCommand('D', D))

			next	= next.append( Merge('merge', split))

			# Optional feedback loop to the split
			next	= next.append( Feedback('feedback', split, err))

		next	= next.append(Command('end'))

		for n in range(5):
			for noise in [0, 0.01, -0.01]:
				pipeline.run(Ctxt(input + noise))
		return

		for n in range(3):
			print(f'{"-"*5} loop-{n} {"-"*5}')
			noise	= 0.05  - float(random.randrange(10))/100.0
			pipeline.run(Ctxt(input + noise))
		return


if __name__ == '__main__':
    unittest.main()
