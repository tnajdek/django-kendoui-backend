from django.test import TestCase
from django.test.client import RequestFactory
from django.db import models
from kendoui_backend.views import KendoListProviderView
import string
import random
import json

class DummyModel(models.Model):
	name = models.CharField(max_length=128)
	number = models.PositiveIntegerField()
	description = models.TextField()

	def __unicode__(self):
		return self.name


class KendoUITest(TestCase):
	
	def setUp(self):
		self.factory = RequestFactory()
		self.view = KendoListProviderView.as_view(model=DummyModel)
	
	def test_empty(self):
		"""
		Test if data provider yields expected result for an empty request
		"""
		request = self.factory.get('/', HTTP_ACCEPT_ENCODING='application/json')
		response = self.view(request)

		response = self.view(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertTrue(json_response.has_key('payload'))
		self.assertEqual(len(json_response['payload']), 0)

	def test_filter_simple(self):
		"""
		Test if data provider correctly applies AND filters
		"""
		for i in range(10):
			DummyModel.objects.create(
			name="%idummy%i" % ((i%3), i),
			number = i,
			description="Some Dummy Description"
		)

		#Take up to 5 items, filter dataset for results where name starts with '1du'
		request = self.factory.get(
			'/?take=5&skip=0&page=1&pageSize=5&filter[logic]=and&filter[filters][0][field]=name&filter[filters][0][operator]=startswith&filter[filters][0][value]=1du',
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertTrue(json_response.has_key('payload'))
		self.assertLessEqual(len(json_response['payload']), 5)

		for item in json_response['payload']:
				self.assertEqual(item['fields']['name'].lower()[:3], '1du')

	def test_filter_with_or_logic(self):	
		"""
		Test if data provider correctly applies OR filters
		"""
		for i in range(10):
			DummyModel.objects.create(
			name="%idummy%i" % ((i%5), i),
			number = i,
			description="Some Dummy Description"
		)

		#Take up to 5 items, filter dataset for results where name start with "1du" or number is greater than 8
		request = self.factory.get(
			'/?take=5&skip=0&page=1&pageSize=5&filter[logic]=or&filter[filters][0][field]=name&filter[filters][0][operator]=startswith&filter[filters][0][value]=1du&filter[filters][1][field]=number&filter[filters][1][operator]=gt&filter[filters][1][value]=8',
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertLessEqual(len(json_response['payload']), 5)

		for item in json_response['payload']:
			if(item['fields']['name'].lower()[:3] == '1du'):
				self.assertEqual(item['fields']['name'].lower()[:3], '1du')
			elif(item['fields']['number']>8):
				self.assertGreater(item['fields']['number'], 8)
			else:
				self.fail()


	def test_sort(self):
		"""
		Test if data provider correctly sorts data.
		"""

		for i in range(10):
			DummyModel.objects.create(
			name=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)),
			number = i,
			description="Some Dummy Description"
		)
		
		#Take 5 items and sort them by name ascending
		request = self.factory.get(
			'/?take=5&skip=0&page=1&pageSize=5&sort[0][field]=name&sort[0][dir]=asc',
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)
		json_response = json.loads(response.content)

		self.assertEquals(json_response['result'], 1)
		self.assertTrue(json_response.has_key('payload'))
		self.assertEqual(len(json_response['payload']), 5)

		last_item = None
		for item in json_response['payload']:
			if(last_item):
				self.assertGreaterEqual(item['fields']['name'], last_item)
			last_item = item['fields']['name']
