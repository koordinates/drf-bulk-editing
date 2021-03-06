#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open

from setuptools import setup, find_packages


setup(
    name='drf-bulk-editing',
    version='0.1.0',
    url='http://www.django-rest-framework.org',
    license='BSD',
    description='Bulk editing for Django REST Framework',
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'six',
        'Django>=1.10',
        # TODO: increase this to DRF 3.7 very soon.
        'djangorestframework>=3.5',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
