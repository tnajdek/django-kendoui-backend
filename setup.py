#!/usr/bin/env python

from distutils.core import setup

setup(	name='django-kendoui-backend',
		version='0.6',
		description='Kendo UI DataSource backend',
		author='Tom Najdek',
		author_email='tom@doppnet.com',
		license='MIT',
		url='https://github.com/irwebuniq/django-kendoui-backend',
		packages=['kendoui_backend'],
		install_requires=[
			'django>=1.9.0',
			'querystring_parser>=1.2.3',
			'six>=1.10.0'
		],
)
