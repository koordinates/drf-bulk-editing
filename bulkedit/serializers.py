# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from six.moves.urllib.parse import urlsplit

from contextlib import contextmanager

from django.db import transaction
from django.urls import resolve, Resolver404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.request import override_method
from rest_framework.generics import GenericAPIView


__all__ = (
    'BulkEditSerializer',
)


class _ActionSerializer(serializers.Serializer):
    """
    Each action has an 'action' key representing an action to take
    against an object.

    Action reference:
        * "create":
            Creates a new object.
            The type of the object can be given by the `url`.
            This should be the URL of a list view where you'd POST to create
            an object normally. The serializer to use for creating the object
            will be retrieved from the view associated with that URL.

            `value` should contain the full content required to create the object

        * "update":
            Partial update of an existing object at the given `url`

        * "delete":
            Delete an existing object at the given `url`. `value` is ignored
            for this action.


    [TODO]: (not implemented yet) Collection actions (manipulating
    membership of a collection):
        * "add"
        * "remove"
        * "append"
        * "insert"
        * "reorder" (??)
    """
    CHOICES_ACTION = ('create', 'update', 'delete')
    _ACTION_METHODS = {
        'create': 'POST',
        'update': 'PUT',
        'delete': 'DELETE',
    }

    # Note: Can't use HyperlinkedIdentityField, because it could be a URL to
    # lots of different types of object, and it could even be a list URL.
    # Also can't use URLField, because the URLValidator requires a TLD,
    # and that breaks in the tests (hostname is 'testserver')
    # So we accept strings, but we validate in `validate_url`
    # (and the hostname must be the same as that of the current request)
    url = serializers.CharField(required=False)
    action = serializers.ChoiceField(CHOICES_ACTION)
    value = serializers.DictField(required=False)

    def allow_bulk_edit_for_view(self, fake_request):
        """
        This is called during serializer validation for each patch to be applied.
        The fake request object corresponding to the individual edit endpoint is provided.

        This should return True if the patch is allowed, and False otherwise.

        The default implementation allows edits to all subresources of the current view.
        i.e. if this view is at /foo/bar/ then:
            * edits to /foo/bar/baz/ are allowed
            * edits to /foo/ aren't allowed.
        """
        current_request = self.context['request']
        return fake_request.path.startswith(current_request.path)

    def validate_url(self, url):
        """
        Validates a URL. Returns a 3-tuple (path, resolver_match, full URLs)
        """
        split = urlsplit(url)

        # Check scheme, hostname and port is the same as the current request
        r = self.context['request']
        current_url = urlsplit(r.build_absolute_uri())
        if tuple(split[:2]) != current_url[:2]:
            raise self.invalid_url(url)

        # Check it's a valid view
        try:
            resolver_match = resolve(split.path)
        except Resolver404:
            raise self.invalid_url(url)

        view = resolver_match.func
        if not hasattr(view, 'view_class') or not issubclass(view.view_class, GenericAPIView):
            # Not a class-based DRF view. Can't easily support this.
            raise self.invalid_url(url)

        return split.path, resolver_match, url

    def invalid_url(self, url):
        raise ValidationError({
            "url": ["URL target is invalid or can't be edited by this endpoint: %s" % url]
        })

    @contextmanager
    def _get_action_view(self, validated_data):
        request = self.context['request']
        path, resolver_match, url = validated_data['url']
        view = resolver_match.func

        # Make a fake request and use that for the view.
        method = self._ACTION_METHODS[validated_data['action']]
        with override_method(view, request, method) as new_request:
            new_request.resolver_match = resolver_match
            new_request.path = path
            new_request._data = new_request._full_data = validated_data['value'] or {}

            # `view` is actually a callback function (see View.as_view)
            # We replace it with our own callback instead,
            # just so we can override initialize_request below
            view_instance = view.view_class(**view.view_initkwargs)
            if hasattr(view_instance, 'get') and not hasattr(view_instance, 'head'):
                view_instance.head = view_instance.get
            view_instance.request = new_request
            view_instance.args = resolver_match.args
            view_instance.kwargs = resolver_match.kwargs

            # DRF's initialize_request() expects a WSGIRequest,
            # and wraps it with a *new* DRF Request object.
            # Instead, we want to keep the existing DRF Request object.
            def _initialize_request(request, *args, **kwargs):
                return request
            view_instance.initialize_request = _initialize_request

            def view_callback():
                return view_instance.dispatch(
                    view.request,
                    *view_instance.args,
                    **view_instance.kwargs
                )

            view_callback.view_instance = view_instance
            yield view_callback

    def to_internal_value(self, data):
        vd = super(_ActionSerializer, self).to_internal_value(data)
        action = vd['action']

        if action != 'delete' and 'value' not in vd:
            raise ValidationError({
                'value': ['This field is required when action is "%s"' % action]
            })

        if 'url' not in vd:
            if action == 'create':
                # POST to the current URL
                r = self.context['request']
                vd['url'] = (r.path, r.resolver_match, r.build_absolute_uri())
            else:
                raise ValidationError({
                    'url': ['This field is required when action is "%s"' % action]
                })

        method = self._ACTION_METHODS[action]

        with self._get_action_view(vd) as view_callback:
            view_instance = view_callback.view_instance

            if method not in view_instance.allowed_methods:
                raise ValidationError({
                    'url': ["This endpoint doesn't accept action='%s'" % action]
                })

            if not self.allow_bulk_edit_for_view(view_instance.request):
                raise self.invalid_url(vd['url'][2])

        return vd

    def apply_action(self, attrs):
        with self._get_action_view(attrs) as view_callback:
            return view_callback()


class BulkEditSerializer(serializers.ListSerializer):
    """
    [De]Serializes a patch comprising multiple actions.
    """
    child = _ActionSerializer()

    def __init__(self, *args, **kwargs):
        okay_statuses = kwargs.pop('only_statuses', range(200, 400))
        super(BulkEditSerializer, self).__init__(*args, **kwargs)
        self.okay_statuses = set(okay_statuses)

    @transaction.atomic
    def apply_bulk_edits(self):
        """
        Apply all actions.
        """
        response_data = []
        statuses = []
        for attrs in self.validated_data:
            response = self.child.apply_action(attrs)
            statuses.append(response.status_code)
            response_data.append(response.data)

        if not self.okay_statuses.issuperset(statuses):
            # TODO: are these full content responses *useful* ?
            # Maybe we should just pass on the *errored* responses
            error_statuses = set(statuses).difference(self.okay_statuses)
            if len(error_statuses) == 1:
                # There was only one unique error status, use that
                status = set(error_statuses).pop()
            elif all(s < 500 for s in error_statuses):
                # The parsing and validation of the request happened okay,
                # but we still received a 4xx error from at least one subresource.
                # We raise a 400 here to keep things simplish.
                status = 400
            else:
                # mixed errors, including server errors
                status = 500
            e = APIException(response_data)
            e.status_code = status
            raise e
        return response_data
