from django.test import TestCase
from utils import get_random_entry
from models import ExampleModel

class ExampleAppTest(TestCase):
	def test_get_random_entry_test(self):
		entry = get_random_entry()
		self.assertEquals(type(entry), ExampleModel)
		self.assertGreater(len(entry.name), 0)
		self.assertGreater(len(entry.description), 0)
		self.assertGreater(entry.number, 0)
		
		
