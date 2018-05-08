# Bulk editing for Django REST Framework

This project allows you to manipulate multiple objects from your API in one request.

Objects must already be exposed to the API, but using this package lets you do several edits in one go, rather than one at a time. Then you can reduce your request overhead and benefit from database transactions.

# Requirements

* Django 1.10+
* Python 2.7 or 3.6

# Limitations

Only class-based API views (subclasses of DRF's `APIView`) may be called by bulk edits. Attempting to call other views will throw validation errors.

# TODO

* tests
* docs

