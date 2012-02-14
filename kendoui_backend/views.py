from django.views.generic import ListView
from json_utils.shortcuts import response_json
from querystring_parser import parser
from django.core.exceptions import FieldError
from django.db.models import Q

class KendoListProviderView(ListView):
	def _build_filters(self, filters, django_filters):
		
		for filter_id in filters:
			filter = filters[filter_id]
			if(filter.has_key('field') and filter.has_key('operator') and filter.has_key('value')):
				if(filter['operator'] == 'startswith' or filter['operator'] == 'endswith'):
					filter['operator'] = 'i'+filter['operator']

				django_filters[filter['field']+'__'+filter['operator']] = filter['value']
		return django_filters

	def _build_sorts(self, sorts, django_sorts, append_default_sorting=True):
		for sort_id in sorts:
			sort = sorts[sort_id]
			if(sort.has_key('field') and sort.has_key('dir')):
				if(sort['dir'].lower() == 'desc'):
					django_sorts.append('-%s' % sort['field'])
				else:
					django_sorts.append(sort['field'])
		if(len(django_sorts) == 0):
			django_sorts.append('id')
		return django_sorts

	def _build_groups(self, groups, django_groups):
		return self._build_sorts(groups, django_groups, False)
		

	def get(self, request, **kwargs):
		arguments = parser.parse(request.GET.urlencode())
		print arguments

		take = arguments.get('take', 10)
		skip = arguments.get('skip', 0)
		total = skip+take
		filter_arg = dict()
		sort_arg = list()
		filter_logic = 'and'

		if(arguments.has_key('filter') and arguments['filter'].has_key('filters')):
			filter_arg = self._build_filters(arguments['filter']['filters'], filter_arg)
			filter_logic = arguments['filter']['logic'].upper()

		if(arguments.has_key('group')):
			sort_arg = self._build_sorts(arguments['group'], sort_arg)

		if(arguments.has_key('sort')):
			sort_arg = self._build_sorts(arguments['sort'], sort_arg)
		
		print sort_arg
		output = dict()

		try:
			filters = Q(**filter_arg)
			filters.connector = filter_logic
			self.queryset = self.model.objects.filter(filters).order_by(*sort_arg)[skip:total]
			output = {'result':1, 'count':self.model.objects.count(), 'payload':self.get_queryset()}
		except FieldError:
			output = {'result':0, 'error':'Invalid request. Tried to filter or sort using invalid field.'}

		return response_json(request, output)
 
