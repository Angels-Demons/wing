from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


def my_get_object_or_return_404(klass, *args, **kwargs):
    try:
        return get_object_or_404(klass, args, kwargs)
    except Http404:
        data = {'message': 'error: not found',
                'code': 200,
                }
        # raise NotFound(detail=data)
        return Response(data, status=HTTP_200_OK)


def _get_queryset(klass):
    """
    Return a QuerySet or a Manager.
    Duck typing in action: any class with a `get()` method (for
    get_object_or_404) or a `filter()` method (for get_list_or_404) might do
    the job.
    """
    # If it is a model class or anything else with ._default_manager
    if hasattr(klass, '_default_manager'):
        return klass._default_manager.all()
    return klass


def my_get_object_or_404(klass, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        data = {'message': 'error: not found',
                'code': 200,
                }
        # return Response(data, status=HTTP_200_OK)
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
