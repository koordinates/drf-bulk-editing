# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework import status
from rest_framework.response import Response

from .serializers import BulkEditSerializer


class BulkEditMixin(object):
    """
    Create a model instance.
    """
    def patch(self, request, *args, **kwargs):
        serializer = self.get_bulk_edit_serializer()

        serializer.is_valid(raise_exception=True)
        self.apply_bulk_edits(serializer)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def get_bulk_edit_serializer(self):
        return BulkEditSerializer(
            # TODO: restrict operations/endpoints
            data=self.request.data,
            context=self.get_serializer_context(),
        )

    def apply_bulk_edits(self, serializer):
        serializer.apply_bulk_edits()
