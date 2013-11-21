#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Apr 6, 2012

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

# ***** Python built-in modules *****
import traceback
import importlib
from types import StringTypes

# ***** Pyramid modules *****
from pyramid.response import Response
from pyramid.httpexceptions import HTTPMethodNotAllowed

# ***** Application modules *****
from .api import ApiDescription
from .api import RepresentationType as ContentType
from .api import ResourceOptionsJSONRepresentation
from .api import RestApiDocJSONRepresentation
from ..errors import ResponseError, ParameterMissedError, NotAcceptableError
from ..http import CommonResponse
from ..utils import parse_body

__author__ = "Greivin Lopez"
__copyright__ = u"Copyright 2012, The Skuë Project"
__credits__ = ["Greivin Lopez"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Greivin Lopez"
__email__ = "greivin.lopez@gmail.com"
__status__ = "Development"


SKUE_CACHE = {}


class BaseHandler(object):
    """Base handler with ACL management.

    Inherit and define the desired methods,
    then register views and set permissions.

    """

    def __init__(self, request):
        self.request = request
        self.response = Response()

    def __call__(self):
        """Dispatch the request."""
        method = self.request.method
        try:
            return getattr(self, method.lower())()
        except (NotImplementedError):
            raise HTTPMethodNotAllowed

    def get(self):
        raise NotImplementedError

    def options(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def put(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


#===============================================================================
# RestResource
#===============================================================================
class RestResource(BaseHandler):
    """The request handler for RESTful controllers."""

    # A dictionary with the parameters of the request regardless of method
    payload = None
    # The list of the required parameters of the request
    required = []
    # The list of the optional parameters of the request
    optional = []
    # String representation of the HTTP method of the current request
    http_method = ''
    # The value of the 'HTTP_USER_AGENT' header
    http_user_agent = ''
    # The RestResourceDescription object that describes this controller options
    resource_description = None
    # The host name of the server
    host_name = None
    # The language the client prefer for the response
    language = 'en'

    def handle_request(self, method, *args, **kwargs):
        """Method that calls the send_response method with the response of
        the resource specific call.

        This function is called with the specific function for the REST
        operation.

        Args:
          method: the method that executes the REST operation
        """
        try:
            self.__entrance()
            return self.send_response(method(*args, **kwargs))
        except ResponseError, error:
            return self.send_response(error.get_http_response())
        except Exception as error:
            # self.logger.exception('An unexpected error has occur')
            return self.handle_unexpected_error(error)

    def __entrance(self):
        """First method executed by every API request

        Will perform common requests stuff such as populating
        internal variables describing the request and loading
        the input parameters and doing automatic validation.
        """
        try:
            # Set the HTTP Method
            self.http_method = self.request.method
            # Set the host name
            self.host_name = self.request.host_url
            # Set the user agent
            user_agent = self.request.user_agent

            if user_agent is not None and isinstance(user_agent, StringTypes):
                self.http_user_agent = user_agent

            # Set the intended response representation
            accepted_format = self.request.headers.get('Accept');
            if accepted_format is not None and not '*/*' in accepted_format:
                self.content_type = accepted_format
            else:
                self.content_type = ContentType.JSON

            # Get the self description of the Resource
            self.resource_description = self.__get_self_description()
            # Load the parameters sent in the HTTP request
            self.__load_parameters()
            # Deduce the expected parameters from description
            self.__deduce_expected_parameters()
            # Validate the request
            self.__validate_request()
            # Validate the parameters
            self.__validate_parameters()
        except Exception as error:
            #self.logger.exception('An unexpected error has occur')
            return self.handle_unexpected_error(error)

    def __get_self_description(self):
        """Gets the description of the resource provided by inheritors.
        It not always create the result from scratch it will first check in
        memory cache object.

        """
        if self.resource_description is not None:
            return self.resource_description
        else:
            method_key = ''.join([self.request.path, '-', self.http_method])
            resource_description = SKUE_CACHE.get(method_key)
            if resource_description is not None:
                self.resource_description = resource_description
                return self.resource_description
            else:
                self.resource_description = self.describe_resource()
                SKUE_CACHE[method_key] = self.resource_description
                return self.resource_description

    def __get_payload(self):
        """Populates payload dictionary from method arguments.

        Retrieve the arguments from the HTTP method and populates
        the payload dictionary of this instance.

        Returns:
          A dict structure with the HTTP request arguments and its values
        """
        payload = {}
        if self.http_method in ('POST', 'PUT'):
            payload = parse_body(self.request.body)
        else:
            for key, value in self.request.params.items():
                payload[key] = value
        return payload

    def __load_parameters(self):
        """Load the parameters of the request.

        Validates the parameters to find missed required parameters or
        unexpected parameters received.

        Raises:
          ParameterMissedError: One of the required parameters is not present
          NotExpectedParameterError: One of the received parameters was not registered
        """
        # Clean the parameter sets.. (unregister previous parameters)
        self.required = []
        self.optional = []

        # Get payload function populates the payload dictionary
        self.payload = self.__get_payload()

    def __deduce_expected_parameters(self):
        """This method it's called every time a request is made.

        It will deduce the different allowed parameters for the current
        request method and which parameters are expected as required
        for the controller to handle validation automatically.
        """
        self_description = self.resource_description
        if self_description is not None:
            methods = self_description.methods
            if methods is not None:
                for method in methods:
                    if method.method == self.http_method:
                        for parameter in method.parameters:
                            if parameter.is_required:
                                self.required.append(parameter.name)
                            else:
                                self.optional.append(parameter.name)

    def __validate_parameters(self):
        """Validate web request parameters.

        Validates the registered parameters against the received parameters
        to determine which required parameters are missed and if there is
        not expected parameters it will remove them from payload.

        Raises:
          ParameterMissedError: One of the required parameters is not present
        """
        # Sets the language of the request if provided
        if 'lang' in self.payload:
            self.language = self.payload['lang']
            del self.payload['lang']

        # Create the needed sets to work with
        required_set = set(self.required)
        optional_set = set(self.optional)
        received_set = set(self.payload.keys())

        # Validate required parameters
        fail_required = required_set - received_set
        if fail_required:
            for expected_parameter in fail_required:
                raise ParameterMissedError(parameter=expected_parameter)

        # Find any invalid params and remove them from self.payload
        valid_set = required_set.union(optional_set)
        invalid_params = received_set - valid_set

        for param in invalid_params:
            del self.payload[param]


    def __validate_request(self):
        """Validates the HTTP request to ensure the ability of
        of this web handler to fulfill the expectations of the
        client with it's response.
        """
        self_description = self.resource_description
        if self_description is not None:
            methods = self_description.methods
            if methods is not None:
                for method in methods:
                    if method.method == self.http_method:
                        if not self.content_type in method.representations:
                            raise NotAcceptableError(method.representations)

    def options_for_resource(self, *args, **kwargs):
        """Retrieves the information related the communication options
        associated to a particular resource

        Returns:
          A self description of the resource in JSON representation
        """
        response_body = ResourceOptionsJSONRepresentation(self.resource_description)
        return CommonResponse.options(self.get_allowed_methods(), response_body)

    def get_allowed_methods(self):
        """Returns a string with the list of HTTP allowed methods"""
        allowed_methods = ""
        if self.resource_description.methods is not None:
            methods_list = [method.method for method in self.resource_description.methods]
            allowed_methods = ', '.join(methods_list)
        return allowed_methods

    def send_response(self, handler_response):
        """Writes an output to the API client with the given response

        Args:
          handler_response: An instance of HandlerHttpResponse that contains
          the data for the response.
        """
        self.response.status_int = handler_response.status_code
        self.response.headerlist = handler_response.headers.iteritems()
        self.response.body = handler_response.write_body()
        return self.response

    def handle_unexpected_error(self, error):
        """Handles the given unexpected error.

        Unexpected error is something that should return a 500 status code
        and also write to log the context and error details.

        Args:
          error: The unexpected error to handle.

        Returns:
          An HTTP 500 error response if not in development environment.
        """
        # return self.error(500)
        raise error.__class__(traceback.format_exc(error))

    #===========================================================================
    # The HTTP Method Handlers
    #===========================================================================
    def get(self, *args, **kwargs):
        """Handler implementation of an HTTP GET method."""
        return self.handle_request(self.read_resource, *args, **kwargs)

    def options(self, *args, **kwargs):
        """Handler implementation of an HTTP OPTIONS method.
        """
        return self.handle_request(self.options_for_resource, *args, **kwargs)

    def post(self, *args, **kwargs):
        """Handler implementation of an HTTP POST method."""
        return self.handle_request(self.create_resource, *args, **kwargs)

    def put(self, *args, **kwargs):
        """Handler implementation of an HTTP PUT method."""
        return self.handle_request(self.update_resource, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Handler implementation of an HTTP DELETE method."""
        return self.handle_request(self.delete_resource, *args, **kwargs)

    #===========================================================================
    # Methods for inheritors
    #===========================================================================
    def create_resource(self, *args, **kwargs):
        """This method should allow users to create new resources.

        Should be implemented by inheritors of this class to create
        new instances of the resource.
        """
        return CommonResponse.method_not_allowed(self.get_allowed_methods())

    def read_resource(self, *args, **kwargs):
        """Retrieve the information of the current resource.
        """
        return CommonResponse.method_not_allowed(self.get_allowed_methods())

    def update_resource(self, *args, **kwargs):
        """Updates the current resource instance.
        """
        return CommonResponse.method_not_allowed(self.get_allowed_methods())

    def delete_resource(self, *args, **kwargs):
        """Removes the resource associated with the given value.
        """
        return CommonResponse.method_not_allowed(self.get_allowed_methods())


#===============================================================================
# DocumentResource
#===============================================================================
class DocumentResource(RestResource):
    """Represents a Document resource. A Document resource is an archetype
    to represent a singular concept.
    Individual items that could be part of a Collection resource.
    """
    pass

#===============================================================================
# StoreDocumentResource
#===============================================================================
class StoreDocumentResource(RestResource):
    """Represents a Document resource. A Document resource is an archetype
    to represent a singular concept.

    The store document differs from the regular document resource because
    it represents individual elements that are part of a Store resource
    so there are some differences in the way this kind of resource should
    handle the HTTP methods.

    Inheritors MUST handle the exists method to indicate if there is
    an existing resource with a provided identification value in order
    to the object to create itself or return it's representation.
    """
    # Will store the URI for a newly created item
    _new_resource_uri = ""

    @property
    def new_resource_uri(self):
        """Return the newly created resource URI"""
        return self._new_resource_uri

    def put(self, *args, **kwargs):
        """Handler implementation of an HTTP PUT method."""
        if len(args) > 0 or len(kwargs) > 0:
            identifier = args[0] if len(args) else kwargs.values()[0]
            if self.exists(identifier):
                # update an existing resource
                super(StoreDocumentResource, self).handle_request(self.update_resource, *args, **kwargs)
            else:
                # create a new resource
                self._new_resource_uri = self.request.path
                super(StoreDocumentResource, self).handle_request(self.create_resource, *args, **kwargs)


    def exists(self, identifier):
        """Gets a value to indicate if the given identifier it's already
        associated to an existing resource.
        This method MUST be implemented for inheritors of this class.

        Args:
          identifier: A value that uniquely identify a resource

        Returns:
          True if the identifier is associated to an existing resource or
          False otherwise.
        """
        return False

#===============================================================================
# CollectionResource
#===============================================================================
class CollectionResource(RestResource):
    """Represents a Collection resource. A Collection resource is a list of
    items or other resources handled by the Server.
    """
    # Will store the offset and limit for pagination in GET requests
    _offset = 0
    _count = 100

    @property
    def offset(self):
        """Return the starting point when retrieving results in a GET"""
        return self._offset

    @property
    def count(self):
        """Return the maximum number of items to return results in a GET"""
        return self._count

    def get(self, *args, **kwargs):
        """Handler implementation of an HTTP GET method."""
        self._offset = int(self.request.params.get("offset", default_value="0"))
        self._count  = int(self.request.params.get("count", default_value="100"))
        super(CollectionResource, self).handle_request(self.read_resource, *args, **kwargs)


#===============================================================================
# StoreResource
#===============================================================================
class StoreResource(RestResource):
    """Represents an Store resource. An Store resource is a collection of
    resources handled by the client.
    """
    def post(self, *args, **kwargs):
        """Handler implementation of an HTTP POST method."""
        super(StoreResource, self).handle_request(self.post_not_allowed, *args, **kwargs)

    def post_not_allowed(self, *args, **kwargs):
        """Returns a response to indicate that the POST method should not
        be allowed on resources of type Store"""
        return CommonResponse.method_not_allowed(self.get_allowed_methods())


#===============================================================================
# ControllerResource
#===============================================================================
class ControllerResource(RestResource):
    """Represents a Controller resource. A Controller resource is a model
    to the concept of a procedure. Some action that is going to be executed
    over other resources but doesn't quite map to the CRUD model.
    """
    def post(self, *args, **kwargs):
        """Handler implementation of an HTTP POST method."""
        super(ControllerResource, self).handle_request(self.execute, *args, **kwargs)

    def execute(self, *args, **kwargs):
        """Performs the execution of the controller's action"""
        return CommonResponse.method_not_allowed(self.get_allowed_methods())


#===============================================================================
# ApiDocumentationResource
#===============================================================================
class ApiDocumentationResource(BaseHandler):
    """A new kind of resource that allows you to self-document your entire API"""

    #===========================================================================
    # The HTTP Method Handlers
    #===========================================================================
    def get(self, *args, **kwargs):
        """Handler implementation of an HTTP GET method."""
        return self.send_response(CommonResponse.method_not_allowed('OPTIONS'))

    def options(self, *args, **kwargs):
        """Handler implementation of an HTTP OPTIONS method.
        """
        self.create_api_documentation(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Handler implementation of an HTTP POST method."""
        return self.send_response(CommonResponse.method_not_allowed('OPTIONS'))

    def put(self, *args, **kwargs):
        """Handler implementation of an HTTP PUT method."""
        return self.send_response(CommonResponse.method_not_allowed('OPTIONS'))

    def delete(self, *args, **kwargs):
        """Handler implementation of an HTTP DELETE method."""
        return self.send_response(CommonResponse.method_not_allowed('OPTIONS'))

    def send_response(self, handler_response):
        """Writes an output to the API client with the given response

        Args:
          handler_response: An instance of HandlerHttpResponse that contains
          the data for the response.
        """
        self.response.status_int = handler_response.status_code
        self.response.headerlist = handler_response.headers.iteritems()
        self.response.body = handler_response.write_body()
        return self.response

    def create_api_documentation(self, *args, **kwargs):
        """Creates the API documentation and return it to consumers"""
        import main
        resources = []
        for web_handler in main.API_HANDLERS:
            try:
                web_handler_instance = web_handler[1]()
            except TypeError:
                # ``webapp2.Route`` class is used for defining routing
                last_dot = web_handler.handler.rindex('.')
                handler_module = web_handler.handler[:last_dot]
                handler_class = web_handler.handler[last_dot + 1:]
                web_handler_instance = getattr(
                    importlib.import_module(handler_module), handler_class)()
            if isinstance(web_handler_instance, RestResource):
                resources.append(web_handler_instance.describe_resource())
            del web_handler_instance

        api_name = main.API_NAME if main.API_NAME else 'API Name Unknown'
        api_description = main.API_DESCRIPTION if main.API_DESCRIPTION else 'No description provided'

        api_documentation = ApiDescription(name=api_name,
                                           resources=resources,
                                           description=api_description)

        response_body = RestApiDocJSONRepresentation(api_documentation)
        return self.send_response(CommonResponse.options('OPTIONS', response_body))
