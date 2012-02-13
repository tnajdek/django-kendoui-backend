from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
from kendoui_backend.views import KendoListProviderView
from app.models import ExampleModel

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
	url(r'^example_model$', KendoListProviderView.as_view(model=ExampleModel), name='example_model'),

    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
