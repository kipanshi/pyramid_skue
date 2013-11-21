#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Apr 3, 2012

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

__author__ = "Greivin Lopez"
__copyright__ = u"Copyright 2012, The Skuë Project"
__credits__ = ["Greivin Lopez"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Greivin Lopez"
__email__ = "greivin.lopez@gmail.com"
__status__ = "Development"


#===============================================================================
# HandlerHttpResponse
#===============================================================================
class HandlerHttpResponse(object):
    """Represents an HTTP response wrapper for the API Server"""

    # A dictionary with the headers to include in the response
    headers = {}
    # The HTTP status code to return
    status_code = None
    # The body for the response: Assume to be a ResponseObject
    body = None
    # The intended "Content-Type" of the response
    _content_type = None

    @property
    def content_type(self):
        """The intended 'Content-Type' of the response"""
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value
        self.headers['Content-Type'] = value

    def __init__(self, status_code, content_type, body="", headers={}):
        """Creates a new HandlerHttpResponse with the given arguments

        Args:
          status_code: The HTTP status code for the response
          content_type: The intended "Content-Type" of the response
          body: A ResourceResponse to use as the body for the response
          headers: A dictionary with the HTTP headers of the response
        """
        self.status_code = status_code
        self.headers = headers
        self.content_type = content_type
        self.body = body

    def write_body(self):
        """Writes out a representation of the body of this HTTP response
        according to the response's Content-Type
        """
        if self.content_type == ContentType.JSON:
            return self.body.as_json()
        else:
            return self.body


#===============================================================================
# CommonResponse
#===============================================================================
class CommonResponse(object):

    @classmethod
    def success(cls, body, content_type=ContentType.JSON):
        http_response = HandlerHttpResponse(status_code=200,
                                            content_type=content_type,
                                            body=body)
        return http_response

    @classmethod
    def simple_success(cls, message, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('Success')
        body.status = "OK"
        body.message = message
        http_response = HandlerHttpResponse(status_code=200,
                                            content_type=content_type,
                                            body=body)
        return http_response

    @classmethod
    def options(cls, allowed_methods, body, content_type=ContentType.JSON):
        http_response = HandlerHttpResponse(status_code=200,
                                            content_type=content_type,
                                            body=body,
                                            headers={"Allow": allowed_methods})
        return http_response

    @classmethod
    def method_not_allowed(cls, allowed_methods,
                           content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('MethodNotAllowed')
        body.status = "Error"
        body.message = "Method Not Allowed"
        http_response = HandlerHttpResponse(status_code=405,
                                            content_type=content_type,
                                            body=body,
                                            headers={"Allow": allowed_methods})
        return http_response

    @classmethod
    def resource_not_found(cls, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('ResourceNotFound')
        body.status = "Error"
        body.message = "The resource could not be found"
        http_response = HandlerHttpResponse(status_code=404,
                                            content_type=content_type,
                                            body=body)
        return http_response

    @classmethod
    def resource_created(cls, resource_uri, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('Success')
        body.status = "OK"
        body.message = "Successfully created"
        body.uri = resource_uri
        http_response = HandlerHttpResponse(
            status_code=201,
            content_type=content_type,
            body=body,
            headers={"Location": resource_uri.encode('ascii', 'ignore')})
        return http_response

    @classmethod
    def resource_creation_queued(cls, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('Success')
        body.status = "OK"
        body.message = "Successfully queued for creation"
        http_response = HandlerHttpResponse(status_code=202,
                                            content_type=content_type,
                                            body=body)
        return http_response

    @classmethod
    def not_acceptable(cls, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('NotAcceptable')
        body.status = "Error"
        body.message = "Not Acceptable"
        http_response = HandlerHttpResponse(status_code=406,
                                            content_type=content_type,
                                            body=body)
        return http_response

    @classmethod
    def custom_validation_error(cls, message, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('CustomError')
        body.status = "Error"
        body.message = message
        http_response = HandlerHttpResponse(status_code=400,
                                            content_type=content_type,
                                            body=body)
        return http_response

    @classmethod
    def custom_server_error(cls, message, content_type=ContentType.JSON):
        body = ResourceJSONRepresentation('CustomError')
        body.status = "Error"
        body.message = message
        http_response = HandlerHttpResponse(status_code=500,
                                            content_type=content_type,
                                            body=body)
        return http_response
