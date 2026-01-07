#!/usr/bin/python
# Filename: Pipeline.py
# Description: Implementation of the Pipeline class

from core.utilities.Patterns import ChainOfResponsibility, Action

class Ctxt:
	def __init__(self, value):
		self.value	= value
		return

	
class Command(Action):
	def __init__(self, name, increment=0.0):
		Action.__init__(self)
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
		Command.__init__(self, name, increment)
		self.paths		= []
		self.feedback	= None
		return
	
	def split(self, cmd):
		path 		= ChainOfResponsibility(cmd)
		self.paths.append( SplitCtxt(path, 0, 0) )
		return path

	def execute(self, ctxt):
		value		= ctxt.value
		if self.feedback is not None:
			value	+= self.feedback

		print(f'{self.name}:{value} - error({self.feedback})')

		for p in self.paths:
			try:
				ctxt.value	= value
				p.result 	= p.path.run(ctxt)
				p.error		= None
			except Exception as e:
				p.error		= e

		return value 
	
class Merge(Command):
	def __init__(self, name, split):
		Command.__init__(self, name, 0)
		self.split		= split
		return

	def execute(self, ctxt):
		return self.merge(ctxt)

	def merge(self, ctxt):
		result		= None
		for p in self.split.action.paths:
			if result is None:
				result	= self.evaluate(ctxt, p)
				continue
			else:
				result	+= self.evaluate(ctxt, p)

		print(f'{self.name}:{result}')
		ctxt.value		= result
		return result
	
	def evaluate(self, ctxt, result):
		return result.result


class Feedback(Command):
	def __init__(self, name, split, errfn):
		Command.__init__(self, name, 0)
		self.split		= split
		self.errfn		= errfn
		return

	def execute(self, ctxt):
		result		= self.errfn(ctxt.value)

		# Feedback the error
		self.split.action.feedback	= result
		print(f'{self.name}:{ctxt.value} -> dx {result}')

		return ctxt.value

class FunctionCommand(Action):
	def __init__(self, name, function):
		Command.__init__(self, name, 0)
		self.fn		= function
		return
	
	def execute(self, ctxt):
		ctxt.value	= self.fn(ctxt.value)
		print(f'{self.name}:{ctxt.value}')
		return ctxt.value


class Pipeline(ChainOfResponsibility):
	def __init__(self, action:Action=None):
		ChainOfResponsibility.__init__(self, action)
		return

		

if __name__ == "__main__":
	test = Pipeline()

