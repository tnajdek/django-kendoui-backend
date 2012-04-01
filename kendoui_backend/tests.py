from django.test import TestCase
from unittest import skipIf
from django.test.client import RequestFactory
from django.db import models
from kendoui_backend.views import KendoListProviderView
import string
import random
import json
from querystring_parser import builder
from django.conf import settings

class DummyModel(models.Model):
	name = models.CharField(max_length=128)
	number = models.PositiveIntegerField()
	description = models.TextField()

	def __unicode__(self):
		return self.name


class DummyRelatedModel(models.Model):
	name = models.CharField(max_length=128)
	related = models.ForeignKey(DummyModel)

class KendoUITest(TestCase):
	
	def setUp(self):
		self.factory = RequestFactory()
		self.view = KendoListProviderView.as_view(model=DummyModel, filters_ci=True)
		self.view2 = KendoListProviderView.as_view(model=DummyRelatedModel, filters_ci=True)
		self.view3 = KendoListProviderView.as_view(model=DummyModel, filters_ci=False)
	
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
		self.assertTrue(json_response.has_key('count'))
		self.assertEquals(json_response['count'], 0)
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

		querystring_data = {
			"take": 5,
			"skip": 0,
			"page": 1,
			"pageSize": 5,
			"filter": {
				"logic": "and",
				"filters": [
					{
						"field": "name",
						"operator": "startswith",
						"value": "1du"
					}
				]
			}
		}

		request = self.factory.get(
			"/?%s" % builder.build(querystring_data),
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertTrue(json_response.has_key('payload'))
		self.assertTrue(json_response.has_key('count'))
		self.assertEquals(json_response['count'], 3) # i = 1,4,7
		self.assertLessEqual(len(json_response['payload']), 5)

		for item in json_response['payload']:
				self.assertEqual(item['fields']['name'].lower()[:3], '1du')

	def test_filter_with_related(self):
		"""
		Test if data provider can correctly handle filters on keys on related models
		"""

		for i in range(10):
			DummyModel.objects.create(
			name="dummy %i" % i,
			number = i,
			description="Some Dummy Description"
		)

		DummyRelatedModel.objects.create(
			name = "needle",
			related = DummyModel.objects.get(number=8)
		)

		DummyRelatedModel.objects.create(
			name = "garbage",
			related = DummyModel.objects.get(number=1)
		)

		querystring_data = {
			'take': 5,
			'skip': 0,
			'page': 1,
			'pageSize': 5,
			'filter': {
				'logic': 'or',
				'filters': [
					{
					'field': 'related.number',
					'operator': 'eq',
					'value': 8
					}
				]
			}
		}

		request = self.factory.get(
			"/?%s" % builder.build(querystring_data),
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view2(request)
		json_response = json.loads(response.content)

		self.assertEquals(json_response['result'], 1)
		self.assertLessEqual(len(json_response['payload']), 1)
		self.assertTrue(json_response.has_key('count'))
		self.assertEquals(json_response['count'], 1)
		self.assertEquals(json_response['payload'][0]['fields']['name'], 'needle')

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

		querystring_data = {
			'skip': 0, 
			'take': 5, 
			'pageSize': 5, 
			'page': 1,
			'filter': {
				'logic': 'or',
				'filters': [
					{'operator': 'startswith', 'field': 'name', 'value': '1du'},
					{'operator': 'gt', 'field': 'number', 'value': 7}
				]
			}
		}

		request = self.factory.get(
			"/?%s" % builder.build(querystring_data),
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertLessEqual(len(json_response['payload']), 5)
		self.assertTrue(json_response.has_key('count'))
		self.assertEquals(json_response['count'], 4) # i= 1,6, 8, 9

		for item in json_response['payload']:
			if(item['fields']['name'].lower()[:3] == '1du'):
				self.assertEqual(item['fields']['name'].lower()[:3], '1du')
			elif(item['fields']['number']>7):
				self.assertGreater(item['fields']['number'], 7)
			else:
				self.fail()

	def test_count(self):
		"""
		Tests if data provider correctly returns total number of matches found
		"""
		for i in range(100):
			DummyModel.objects.create(
			name="%idummy" % (i%3),
			number = i,
			description="Some Dummy Description"
		)

		querystring_data = {
			"take": 10,
			"skip": 0,
			"page": 1,
			"pageSize": 10,
			"filter": {
				"logic": "and",
				"filters": [
					{
						"field": "name",
						"operator": "startswith",
						"value": "1du"
					}
				]
			}
		}


		request = self.factory.get(
			"/?%s" % builder.build(querystring_data),
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertEquals(len(json_response['payload']), 10)
		self.assertTrue(json_response.has_key('count'))
		self.assertEquals(json_response['count'], 33)


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

		querystring_data = {
			'skip': 0,
			'take': 5,
			'pageSize': 5,
			'page': 1,
			'sort': [
				{'field': 'name', 'dir': 'asc'},
			]
		}
		
		request = self.factory.get(
			"/?%s" % builder.build(querystring_data),
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

	@skipIf(settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3', "SQLITE can't support case-sensitive LIKE")
	def test_filter_cs(self):
		"""
		Test if data provider correctly understands case-insensitive filters
		"""
		for i in range(10):
			DummyModel.objects.create(
			name="dummy%i" % i,
			number = i,
			description = "aa DoPPler aa" if i % 3 == 1 else "aa doppler aa"
		)

		querystring_data = {
			"take": 5,
			"skip": 0,
			"page": 1,
			"pageSize": 5,
			"filter": {
				"logic": "and",
				"filters": [
					{
						"field": "description",
						"operator": "contains",
						"value": "DoPPler"
					}
				]
			}
		}

		request = self.factory.get(
			"/?%s" % builder.build(querystring_data),
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view3(request)
		json_response = json.loads(response.content)
		self.assertEquals(json_response['result'], 1)
		self.assertTrue(json_response.has_key('payload'))
		self.assertTrue(json_response.has_key('count'))
		self.assertEquals(json_response['count'], 3) # i = 1,4,7
		self.assertEquals(len(json_response['payload']), 3)

		for item in json_response['payload']:
			self.assertEqual(item['fields']['description'], 'aa DoPPler aa')
