# Bulk editing for Django REST Framework

This project allows you to manipulate multiple objects from your API in one request.

Each action must already be exposed to the API, but using this package lets you do several actions in one go, rather than one at a time. Then you can reduce your request overhead and benefit from database transactions.

# Usage

Just subclass `BulkEditMixin` for your list & create view:

```python
# URL: /flobbits/
class FlobbitListAndCreate(BulkEditMixin, ListCreateAPIView):
    def post(self, request, *args, **kwargs):
        """
        Create a Flobbit.
        """
```

Then start using `PATCH` requests, with a list of changes to apply:

```json
PATCH /flobbits/
[
    {
        "action": "create",
        "value": {
            "name": "King Flerb the Flobnaminous",
            "points": 99
        }
    },
    {
        "action": "delete",
        "url": "/flobbits/1/",
        "value": {
            "name": "Florious the Tyrant",
            "points": 0
        }
    },
    {
        "action": "update",
        "url": "/flobbits/2/",
        "value": {
            "name": "Dave"
        }
    }
]
```

The above is essentially the same as:
 * `POST /flobbits/`
 * `DELETE /flobbits/1/`
 * `PUT /flobbits/2/`

# Development Status

This project is in early development and will change quickly. No guarantees about API stability.

# Notes

1. The actual views are called, so access permissions etc are respected.
2. The entire update is run in a transaction.
3. Response status codes:
    * Successful patches always receive a `204 No Content` response.
    * If only one unique error response code is returned, the entire patch receives that response code.
    * If there are more than one unique error code, the entire patch receives a 500 or 400 response (depending on whether there were any 5xx errors)
4. By default, the actions are limited to subresources (so a `PATCH` to `/flobbits/` won't accept actions with `"url": "/other/"`.)

# Limitations

Only URLs pointing to class-based generic API views (subclasses of DRF's `GenericAPIView`) may be called by bulk actions. Attempting to call other views will throw validation errors.

# Requirements

- Any supported version of:
    * Python
    * Django
    * Django REST Framework
- `six`
