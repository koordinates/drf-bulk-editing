# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import json

import pytest
from mock import patch

from django.conf.urls import url
from rest_framework.response import Response
from rest_framework.views import APIView

from bulkedit.mixins import BulkEditMixin


def non_apiview(request):
    raise NotImplementedError('view called, unexpected')


class FlobbitDetail(APIView):
    def post(self, request, *args, **kwargs):
        raise NotImplementedError('view called, unexpected')

    def put(self, request, *args, **kwargs):
        raise NotImplementedError('view called, unexpected')


class FlobbitListAndCreate(BulkEditMixin, APIView):
    def post(self, request, *args, **kwargs):
        raise NotImplementedError('view called, unexpected')


urlpatterns = [
    url(r'^non-apiview/', non_apiview),
    url(r'^flobbits/', FlobbitListAndCreate.as_view()),
    url(r'^flobbits/(?P<flobbit_id>\d+)/$', FlobbitDetail.as_view()),
]


@pytest.mark.urls('tests.test_serializers')
def test_bulk_create_ok(client):
    action = {
        # no url, defaults to /flobbits/
        'action': 'create',
        'value': {'a': 'b'},
    }
    a_201 = Response({}, status=201)
    with patch.object(FlobbitListAndCreate, 'post', return_value=a_201) as create_view:
        response = client.patch(
            '/flobbits/',
            json.dumps([action]),
            content_type='application/json'
        )
        create_view.assert_called_once()

        # Successful bulk action has no content
        assert response.status_code == 204
