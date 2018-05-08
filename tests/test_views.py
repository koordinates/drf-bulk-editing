# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import json

import pytest
from mock import patch

from django.conf.urls import url
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from bulkedit.mixins import BulkEditMixin


def non_apiview(request):
    raise NotImplementedError('view called, unexpected')


class FlobbitDetail(GenericAPIView):
    def put(self, request, *args, **kwargs):
        raise NotImplementedError('view called, unexpected')

    def delete(self, request, *args, **kwargs):
        raise NotImplementedError('view called, unexpected')


class FlobbitListAndCreate(BulkEditMixin, GenericAPIView):
    def post(self, request, *args, **kwargs):
        raise NotImplementedError('view called, unexpected')


urlpatterns = [
    url(r'^non-subresource/$', FlobbitListAndCreate.as_view()),
    url(r'^flobbits/$', FlobbitListAndCreate.as_view()),
    url(r'^flobbits/(?P<flobbit_id>\d+)/$', FlobbitDetail.as_view()),
    url(r'^flobbits/non-apiview/$', non_apiview),
]


@pytest.mark.urls('tests.test_views')
def test_patch_for_non_apiview(client):
    action = {
        'url': 'http://testserver/non-apiview/',
        'action': 'create',
        'value': {'flerbies': 99},
    }
    with patch.object(FlobbitListAndCreate, 'post') as create_view:
        # This causes a validation error, because the URL
        # in the action is not supported (it isn't a subresource of /flobbits/)
        response = client.patch(
            '/flobbits/',
            json.dumps([action]),
            content_type='application/json'
        )
        create_view.assert_not_called()
        assert response.status_code == 400


@pytest.mark.urls('tests.test_views')
def test_patch_for_non_subresource(client):
    action = {
        'url': 'http://testserver/non-subresource/',
        'action': 'create',
        'value': {'flerbies': 99},
    }
    with patch.object(FlobbitListAndCreate, 'post') as create_view:
        # This causes a validation error, because the URL
        # in the action is not supported (it isn't a subresource of /flobbits/)
        response = client.patch(
            '/flobbits/',
            json.dumps([action]),
            content_type='application/json'
        )
        create_view.assert_not_called()
        assert response.status_code == 400


@pytest.mark.urls('tests.test_views')
def test_patch_wrong_action(client):
    action = {
        'url': 'http://testserver/flobbits/1/',
        'action': 'create',
        'value': {'flerbies': 99},
    }
    # This causes a validation error, because the action is wrong
    # (the given view doesn't support 'create' because it's a detail view.)
    response = client.patch(
        '/flobbits/',
        json.dumps([action]),
        content_type='application/json'
    )
    assert response.status_code == 400


@pytest.mark.urls('tests.test_views')
def test_patch_create_ok(client, db):
    action = {
        # no url, defaults to http://testserver/flobbits/
        'action': 'create',
        'value': {'flerbies': 99},
    }
    a_201 = Response({}, status=201)
    with patch.object(FlobbitListAndCreate, 'post', return_value=a_201) as create_view:
        response = client.patch(
            '/flobbits/',
            json.dumps([action]),
            content_type='application/json'
        )
        create_view.assert_called_once()

        assert response.status_code == 204


@pytest.mark.urls('tests.test_views')
def test_patch_update_ok(client, db):
    action = {
        'url': 'http://testserver/flobbits/1/',
        'action': 'update',
        'value': {'flerbies': 99},
    }
    a_200 = Response({}, status=200)
    with patch.object(FlobbitDetail, 'put', return_value=a_200) as update_view:
        response = client.patch(
            '/flobbits/',
            json.dumps([action]),
            content_type='application/json'
        )
        assert response.status_code == 204
        update_view.assert_called_once()


@pytest.mark.urls('tests.test_views')
def test_patch_delete_ok(client, db):
    action = {
        'url': 'http://testserver/flobbits/1/',
        'action': 'delete',
        # no value required
    }
    a_204 = Response({}, status=204)
    with patch.object(FlobbitDetail, 'delete', return_value=a_204) as delete_view:
        response = client.patch(
            '/flobbits/',
            json.dumps([action]),
            content_type='application/json'
        )
        assert response.status_code == 204
        delete_view.assert_called_once()
