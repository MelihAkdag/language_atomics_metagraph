#!/usr/bin/python
# Filename: test_Knowledge.py
# Description: Test cases for the Knowledge class

from cor.knowledge.Knowledge import Knowledge

import unittest

class KnowledgeTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		return
		
	@classmethod
	def tearDownClass(self):
		return
		
	def setUp(self):
		self.kb = Knowledge('graph')
		#self.setup_db()
		return
		
	def tearDown(self):
		return

	def setup_db(self):
		lang = self.kb.speak()
		'''					
			Melih {
				is man;	
				is father;
				has home  Melih.Home
			}

			Melih.Home{
				has address "23.Dalcant.Trondheim"
				is house;
			}

			Sreekant {
				is man;	
				has home  Sreekant.Home
			}

			Sreekant.Home{
				has address "26.ChhatraMarg.Delhi"
				is house;
			}

			man {
				is male
				has description 'Is a male'
			};

			father {
				is male
			}
		'''
		say = self.kb.speak()
		
		say.IS('Sreekant', 'man')
		say.IS('Melih', 'man')
		say.IS('Melih', 'father')
		say.HAS('Melih', 'home', 'Melih.Home')
		say.HAS('Melih.Home', 'address', '23.Dalcant.Trondheim')
		say.IS('Melih.Home', 'house')
		say.IS('man', 'male')
		say.HAS('man', 'description', 'Is a male')
		say.IS('23.Dalcant.Trondheim', 'house')
		say.HAS('Sreekant', 'home', 'Sreekant.Home')
		say.HAS('Sreekant.Home', 'address', '26.ChhatraMarg.Delhi')
		say.IS('Sreekant.Home', 'house')
		say.IS('father', 'male')
		return

	def test_add(self):
		sreekant = self.kb['Sreekant']
		melih = self.kb['Melih']
		self.assertEqual(sreekant['name'], 'Sreekant')
		self.assertEqual(melih['name'], 'Melih')

	def test_load(self):
		c = self.kb.slice('Melih', depth=2)

		print( f'vertices = {len(c.vertices)}' )
		print( c )
		return

	def test_load(self):
		c = self.kb.get_all()
		print( f'vertices = {len(c.vertices)}' )
		print( c )
		return

if __name__ == '__main__':
    unittest.main()
