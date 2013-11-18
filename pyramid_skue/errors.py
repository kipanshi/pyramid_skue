#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Apr 2, 2012

@author: Greivin Lopez
'''

# Copyright (c) 2012 The Skuë Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# ***** Application modules *****
from .json.utils import ResourceJSONRepresentation
from .rest.api import RepresentationType as ContentType
from .http import HandlerHttpResponse

__author__ = "Greivin Lopez"
__copyright__ = u"Copyright 2012, The Skuë Project"
__credits__ = ["Greivin Lopez"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Greivin Lopez"
__email__ = "greivin.lopez@gmail.com"
__status__ = "Development"


#===============================================================================
# ResponseError
#===============================================================================
class ResponseError(Exception):
    """Represents a response error.

    This is the base class for all the response errors.
    Mainly errors we want to send to the user as HTTP error responses.
    All the server errors that should be presented to the requester client
    should inherit from this exception.
    """
    #@summary: The HTTP status code of the error
    code = None

    def __init__(self, code):
        """Creates a new instance of the ResponseError with the given
        arguments.

        Args:
          code: An alias to identify the error.
          source: The name of the class that generates the error.
        """
        self.code = code

    def __str__(self):
        """
        To provide a more custom display in our exceptions overriding this
        method allows us to return our dynamically constructed error message.
        """
        return self.message

    @property
    def message(self):
        """Text representation of this error.

        This represents the message to send to the client. It is a more
        detailed description of the error.
        It is intended to be returned as the description value of the
        error in the HTTP response.
        """
        return "An unknown error has occurred."

    def get_http_response(self, content_type=ContentType.JSON):
        """Creates an HandlerHttpResponse with JSON content to output
        this API handler error to a client.
        """
        body = ResourceJSONRepresentation('ApiHandledError')
        body.status = "Error"
        body.message = self.message
        http_response = HandlerHttpResponse(status_code=self.code,
                                           content_type=content_type,
                                           body=body)
        return http_response

#===============================================================================
# ParameterMissedError
#===============================================================================
class ParameterMissedError(ResponseError):
    """A required parameter is missed from an API call.
    """
    #@summary: The name of the parameter that is missed in the endpoint call.
    parameter = None

    @property
    def message(self):
        return "The %s parameter is missed." % self.parameter

    def __init__(self, parameter):
        ResponseError.__init__(self, code=400)
        self.parameter = parameter


#===============================================================================
# NotExpectedParameterError
#===============================================================================
class NotExpectedParameterError(ResponseError):
    """A given parameter is not registered as expected from an API call.
    """
    #@summary: The name of the parameter that was not expected but received.
    parameter = None

    @property
    def message(self):
        return "The %s parameter is not expected." % self.parameter

    def __init__(self, parameter):
        ResponseError.__init__(self, code=400)
        self.parameter = parameter

#===============================================================================
# InvalidParameterFormatError
#===============================================================================
class InvalidParameterFormatError(ResponseError):
    """An error to be raise when a given parameter does not conform with
    the expected formating of that parameter.
    """
    #@summary: The name of the parameter received with an invalid format.
    parameter = None

    @property
    def message(self):
        return "Invalid format for parameter %s." % self.parameter

    def __init__(self, parameter):
        ResponseError.__init__(self, code=400)
        self.parameter = parameter

#===============================================================================
# UnknownReferenceError
#===============================================================================
class UnknownReferenceError(ResponseError):
    """Response error when a given reference could not be found in the storage.

    Error response when a given parameter value representing a reference could
    not be found in the storage.
    """
    #@summary: The name of the parameter associated to this error
    name = None
    #@summary: The value of the parameter that could not be found in the storage
    value = None

    @property
    def message(self):
        return 'The %s=%s cannot be found into the storage.' % (self.name, self.value)

    def __init__(self, name, value):
        """Creates a new UnknownReferenceError."""
        ResponseError.__init__(self, code=404)
        self.name = name
        self.value = value

#===============================================================================
# NotAcceptableError
#===============================================================================
class NotAcceptableError(ResponseError):
    """Response error when detected a request that cannot be fullfil by the
    request handler.
    """
    #@summary: The supported representation for a resource
    supported_representations = ''

    @property
    def message(self):
        return 'The resource only supports the following representations: %s' % (self.supported_representations)

    def __init__(self, supported_representations):
        """Creates a new UnknownReferenceError."""
        ResponseError.__init__(self, code=406)
        self.supported_representations = supported_representations
