#!/usr/bin/env python

from distutils.core import setup

setup(	name='django-kendoui-backend',
		version='0.4',
		description='Kendo UI DataSource backend',
		author='Tom Najdek',
		author_email='tom@doppnet.com',
		license='MIT',
		url='https://github.com/tnajdek/django-kendoui-backend',
		packages=['kendoui_backend'],
		install_requires=[
			'django>=1.3.0',
			'json_utils>=0.2',
			'querystring_parser>=1.1'
		],
)
