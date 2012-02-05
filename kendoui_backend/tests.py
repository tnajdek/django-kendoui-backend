from django.test import TestCase
from django.test.client import RequestFactory
from django.db import models
from kendoui_backend.views import KendoListProviderView

class DummyModel(models.Model):
	name = models.CharField(max_length=128)
	number = models.PositiveIntegerField()
	description = models.TextField()

	def __unicode__(self):
		return self.title


class KendoUITest(TestCase):
	
	def setUp(self):
		self.factory = RequestFactory()
		self.view = KendoListProviderView.as_view(model=DummyModel)
	
	def test_empty(self):
		request = self.factory.get('/', HTTP_ACCEPT_ENCODING='application/json')
		response = self.view(request)

		expected_response = '.*?\{"count": 0, "result": 1, "payload": \[\]\}'
		self.assertRegexpMatches(
			str(response),
			expected_response
		)

	def test_and(self):
		for i in range(10):
			DummyModel.objects.create(
			name="%idummy%i" % ((i%3), i),
			number = i,
			description="Some Dummy Description"
		)

		request = self.factory.get(
			'/?take=5&skip=0&page=1&pageSize=5&filter[logic]=and&filter[filters][0][field]=name&filter[filters][0][operator]=startswith&filter[filters][0][value]=1du',
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)

		expected_response = '.*?\{"count": 10, "result": 1, "payload": \[\{"pk": \d+, "model": "kendoui_backend.dummymodel", "fields": \{"description": "Some Dummy Description", "name": "1dummy1", "number": 1\}\}, \{"pk": \d+, "model": "kendoui_backend.dummymodel", "fields": \{"description": "Some Dummy Description", "name": "1dummy4", "number": 4\}\}, \{"pk": \d+, "model": "kendoui_backend.dummymodel", "fields": \{"description": "Some Dummy Description", "name": "1dummy7", "number": 7\}\}\]\}'
		self.assertRegexpMatches(
			str(response),
			expected_response
		)

	def test_or(self):	
		for i in range(10):
			DummyModel.objects.create(
			name="%idummy%i" % ((i%5), i),
			number = i,
			description="Some Dummy Description"
		)
		request = self.factory.get(
			'/?take=5&skip=0&page=1&pageSize=5&filter[logic]=or&filter[filters][0][field]=name&filter[filters][0][operator]=startswith&filter[filters][0][value]=1du&filter[filters][1][field]=number&filter[filters][1][operator]=gt&filter[filters][1][value]=8',
			HTTP_ACCEPT_ENCODING='application/json'
		)

		response = self.view(request)

		expected_response = '.*?\{"count": 10, "result": 1, "payload": \[\{"pk": \d+, "model": "kendoui_backend.dummymodel", "fields": \{"description": "Some Dummy Description", "name": "1dummy1", "number": 1\}\}, \{"pk": \d+, "model": "kendoui_backend.dummymodel", "fields": \{"description": "Some Dummy Description", "name": "1dummy6", "number": 6\}\}, \{"pk": \d+, "model": "kendoui_backend.dummymodel", "fields": \{"description": "Some Dummy Description", "name": "4dummy9", "number": 9\}\}\]\}'
		self.assertRegexpMatches(
			str(response),
			expected_response
		)

	def test_sort(self):
		pass