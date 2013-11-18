#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Apr 5, 2012

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
from ..json.utils import ResourceJSONRepresentation

__author__ = "Greivin Lopez"
__copyright__ = u"Copyright 2012, The Skuë Project"
__credits__ = ["Greivin Lopez"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Greivin Lopez"
__email__ = "greivin.lopez@gmail.com"
__status__ = "Development"


#===============================================================================
# RepresentationType
#===============================================================================
class RepresentationType(object):
    """A collection of constants to describe the different values that could
    be use as the Internet media type in Content-Type HTTP headers.

    Use this values as:
    from skue.rest.api import RepresentationType as MediaType

    if self.representation == MediaType.JSON:
        return output.as_json()

    @see: http://en.wikipedia.org/wiki/Internet_media_type
    """
    # @ivar JSON: JavaScript Object Notation media type
    JSON = "application/json"

    # @ivar ATOM: Atom feeds media type
    ATOM = "application/atom+xml"

    # @ivar TEXT: Textual data media type. Defined in RFC 2046 and RFC 3676
    TEXT = "text/plain"

    # @ivar XML: Extensible Markup Language (XML) media type
    XML = "application/xml"

    # @ivar JPEG:  JPEG JFIF image media type. Defined in RFC 2045 and RFC 2046
    JPEG = "image/jpeg"

    # @ivar PNG: Portable Network Graphics media type. Defined in RFC 2083
    PNG =  "image/png"


#===============================================================================
# ApiDescription
#===============================================================================
class ApiDescription(object):
    """Represents a self descriptive object to document a REST API"""
    _name = ''
    _resources = []
    _description = ''

    @property
    def name(self):
        """The name of the API"""
        return self._name

    @property
    def resources(self):
        """The list of the resources associated to the API"""
        return self._resources

    @property
    def description(self):
        """The description of the API"""
        return self._description

    def __init__(self, name, resources, description):
        """Create a new object that self-document an API

        Args:
          name: The name of the API
          resources: The list of ResourceDescription objects to describe
                     the available resources for the API
          description: A textual description of the API
        """
        self._name = name
        self._resources = resources
        self._description = description


#===============================================================================
# ResourceDescription
#===============================================================================
class ResourceDescription(object):
    """Represents a self descriptive object to document a REST resource
    handler (controller).
    """
    _name = ''
    _url = ''
    _methods = []
    _description = ''

    @property
    def name(self):
        """The name of the resource"""
        return self._name

    @property
    def url(self):
        """The URL where clients can interact with the resource"""
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def methods(self):
        """The list of methods available to interact with the resource"""
        return self._methods

    @methods.setter
    def methods(self, value):
        self._methods = value

    @property
    def description(self):
        """A description for the resource"""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def __init__(self, name, url = '', methods = [], description = ''):
        """Creates a new description for the options to interact with a
        resource.

        Args:
          name: The name of the resource
          url: The url where the clients can interact with the resource
          methods: The list of HttpMethodDescription objects to describe
                   the available methods for the resource
          description: A textual description of the resource
        """
        self._name = name
        self.url = url
        self.methods = methods
        self.description = description

#===============================================================================
# HttpMethodDescription
#===============================================================================
class HttpMethodDescription(object):
    """Represents a self descriptive object to document an HTTP Method"""
    _method = ''
    _parameters = []
    _representations = [RepresentationType.JSON]
    _languages = []
    _description = ''
    _example_uri = ''

    @property
    def method(self):
        """The name of the HTTP method"""
        return self._method

    @property
    def parameters(self):
        """The list of the HttpParameterDescription objects to describe
        the parameters of this HTTP method
        """
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def representations(self):
        """The media type representations supported for the method"""
        return self._representations

    @representations.setter
    def representations(self, value):
        self._representations = value

    @property
    def languages(self):
        """The language representations supported for the method"""
        return self._languages

    @languages.setter
    def languages(self, value):
        self._languages = value

    @property
    def description(self):
        """A description of the purpose of the HTTP method"""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def example_uri(self):
        """URI of a valid example for an HTTP GET over the resource"""
        return self._example_uri

    @example_uri.setter
    def example_uri(self, value):
        self._example_uri = value

    def __init__(self,
                 method,
                 parameters = [],
                 representations=[RepresentationType.JSON],
                 languages = [],
                 description = '',
                 example_uri = ''):
        """
        Creates a new description for an HTTP method with the given arguments

        Args:
          method: The name of the HTTP method to describe
          parameters: A list of HTTPParameterDescription objects with the
                      description of this method's parameters
          representations: The list of Internet Media Types supported as the
                          representations of the resource for the HTTP method.
          languages: The list of supported languages to represent the response
                     for the HTTP method.
          description: A textual description of the method.
          example_uri: The URI of a valid GET example (for GET methods only)
        """
        self._method = method
        self.parameters = parameters
        self.representations = representations
        self.languages = languages
        self.description = description
        self.example_uri = example_uri


#===============================================================================
# HttpParameterDescription
#===============================================================================
class HttpParameterDescription(object):
    """Represents a self descriptive object to document an HTTP parameter
    of an HTTP Method request.
    """
    _name = ''
    _parameter_type = 'string'
    _is_required = False
    _description = ''

    @property
    def name(self):
        """The name of the HTTP parameter"""
        return self._name

    @property
    def parameter_type(self):
        """The type of the HTTP parameter"""
        return self._parameter_type

    @parameter_type.setter
    def parameter_type(self, value):
        self._parameter_type = value

    @property
    def is_required(self):
        """A value indicating if the HTTP parameter is required or not"""
        return self._is_required

    @is_required.setter
    def is_required(self, value):
        self._is_required = value

    @property
    def description(self):
        """A description of the HTTP parameter meaning and purpose"""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def __init__(self, name, parameter_type = 'string', is_required = False, description = ''):
        """
        Creates a new description for an HTTP method parameter with the
        given arguments.

        Args:
          name: The name of the parameter
          parameter_type: The expected 'type' for the parameter
          is_required: True if the parameter is required, False otherwise
          description: A brief description of the parameter meaning and use
        """
        self._name = name
        self.parameter_type = parameter_type
        self.is_required = is_required
        self.description = description

#===============================================================================
# ParameterOptionsJSONRepresentation
#===============================================================================
class ParameterOptionsJSONRepresentation(ResourceJSONRepresentation):
    """The response to show a method parameter"""
    def __init__(self, parameter):
        ResourceJSONRepresentation.__init__(self, 'HttpParameter')
        self.name = parameter.name
        self.type = parameter.parameter_type
        self.required = parameter.is_required
        self.description = parameter.description

#===============================================================================
# MethodOptionsJSONRepresentation
#===============================================================================
class MethodOptionsJSONRepresentation(ResourceJSONRepresentation):
    """The response to show the options for a particular method"""
    def __init__(self, method):
        ResourceJSONRepresentation.__init__(self, 'HttpMethod')
        self.method = method.method
        self.description = method.description
        if method.method == 'GET' and method.example_uri is not None and len(method.example_uri) > 0:
            self.example = ''.join(['http://jsonviewer.stack.hu/#', method.example_uri])
        self.parameters = [ParameterOptionsJSONRepresentation(parameter) for parameter in method.parameters]

#===============================================================================
# ResourceOptionsJSONRepresentation
#===============================================================================
class ResourceOptionsJSONRepresentation(ResourceJSONRepresentation):
    """The response to show the options for a particular resource"""
    def __init__(self, rest_resource_description):
        ResourceJSONRepresentation.__init__(self, 'RESTResource')
        self.name = rest_resource_description.name
        self.url = rest_resource_description.url
        self.description = rest_resource_description.description
        self.methods = [MethodOptionsJSONRepresentation(method) for method in rest_resource_description.methods]

#===============================================================================
# RestApiDocJSONRepresentation
#===============================================================================
class RestApiDocJSONRepresentation(ResourceJSONRepresentation):
    """The response to show the options for the entire API"""
    def __init__(self, api_description):
        ResourceJSONRepresentation.__init__(self, 'RESTAPI')
        self.name = api_description.name
        self.description = api_description.description
        self.resources = [ResourceOptionsJSONRepresentation(resource) for resource in api_description.resources]

