#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open

from setuptools import setup, find_packages


setup(
    name='drf-bulk-editing',
    version='0.0.dev1',
    url='http://www.django-rest-framework.org',
    license='BSD',
    description=open('README.md', 'r').read(),
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['six'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
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
