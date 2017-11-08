"""
Custom Exceptions and Custom Exception Handler
"""
from __future__ import unicode_literals
import logging

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.exceptions import APIException
from rest_framework.compat import set_rollback
from rest_framework.response import Response

logger = logging.getLogger('ozp-center.' + str(__name__))


class NotFound(Http404):
    pass


class PermissionDenied(PermissionDenied):
    pass


class InvalidInput(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid Input')
    default_code = 'invalid_input'


class RequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Request Exception')
    default_code = 'request'


class AuthorizationFailure(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Not authorized to view')
    default_code = 'authorization_failure'


class ElasticsearchServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Elasticsearch Service Unavailable')
    default_code = 'elasticsearch_unavailable'


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.
    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.
    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    request = context.get('request')
    logger.exception(exc, extra={'request': request})

    if isinstance(exc, APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        # TODO: Investigate
        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'error': True, 'detail': exc.detail, 'error_code': exc.default_code}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        msg = _('Not found.')
        data = {'error': True, 'detail': six.text_type(msg), 'error_code': 'not_found'}

        set_rollback()
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, ObjectDoesNotExist):
        msg = _('Object Not found.')
        data = {'error': True, 'detail': six.text_type(msg), 'error_code': 'not_found'}

        set_rollback()
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, PermissionDenied):
        msg = _('Permission denied.')
        data = {'error': True, 'detail': six.text_type(msg), 'error_code': 'permission_denied'}

        message = six.text_type(exc)
        if message:
            data['detail'] = message

        set_rollback()
        return Response(data, status=status.HTTP_403_FORBIDDEN)
    # Note: Unhandled exceptions will raise a 500 error.
    return None
