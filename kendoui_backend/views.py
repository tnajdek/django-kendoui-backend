from django.views.generic import ListView
from django.http import JsonResponse
from querystring_parser import parser
from django.core.exceptions import FieldError


class KendoListProviderView(ListView):
	filters_ci = True
	distinct = False

	def _build_filters(self, filters, django_filters):
		for filter_id in filters:
			filter = filters[filter_id]
			if(('field' in filter) and ('operator' in filter) and ('value' in filter)):
				if(self.filters_ci and (filter['operator'] == 'startswith' or filter['operator'] == 'endswith' or filter['operator'] == 'contains')):
					filter['operator'] = 'i' + filter['operator']
					
				if "." in filter['field']:
					filter['field'] = filter['field'].replace('.', '__')
					django_filters[filter['field']] = filter['value']
				elif(filter['operator'] == 'eq'):
					django_filters[filter['field']] = filter['value']
				else:
					django_filters[filter['field'] + '__' + filter['operator']] = filter['value']
		return django_filters

	def _build_sorts(self, sorts, django_sorts, append_default_sorting=True):
		for sort_id in sorts:
			sort = sorts[sort_id]
			if(('field' in sort) and ('dir' in sort)):
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

		take = int(arguments.get('take', 10))
		skip = int(arguments.get('skip', 0))
		total = skip + take
		filter_arg = dict()
		sort_arg = list()
		filter_logic = 'and'

		if(("filter" in arguments) and ('filters' in arguments['filter'])):
			filter_arg = self._build_filters(arguments['filter']['filters'], filter_arg)
			filter_logic = arguments['filter']['logic'].upper()

		if('group' in arguments):
			sort_arg = self._build_sorts(arguments['group'], sort_arg)

		if('sort' in arguments):
			sort_arg = self._build_sorts(arguments['sort'], sort_arg)

		output = dict()

		try:
			filters = Q(**filter_arg)
			filters.connector = filter_logic
			items = self.model.objects.filter(filters).order_by(*sort_arg)


			if(self.distinct):
				items = items.distinct()
			self.queryset = items[skip:total]
			output = {'success':True, 'Aggregates':{},'Total':items.count(), 'Data' : list(self.get_queryset().values())}
		except FieldError:
			output = {'success': False, 'Data':'', 'error':'Invalid request. Tried to filter or sort using invalid field.'}

		return JsonResponse(output,  safe=False)