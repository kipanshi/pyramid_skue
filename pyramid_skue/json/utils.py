#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Mar 6, 2012

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
import json

__author__ = "Greivin Lopez"
__copyright__ = u"Copyright 2012, The Skuë Project"
__credits__ = ["Greivin Lopez"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Greivin Lopez"
__email__ = "greivin.lopez@gmail.com"
__status__ = "Development"


#===============================================================================
# ResourceJSONEncoder
#===============================================================================
class ResourceJSONEncoder(json.JSONEncoder):
    '''Custom JSON Encoder to serialize complex objects'''
    def default(self, obj):
        if isinstance(obj, ResourceJSONRepresentation):
            response = {}
            for field in dir(obj):
                if not field.startswith('_') and not field in obj.exclude:
                    response[field] = getattr(obj, field)
            return response
        return json.JSONEncoder.default(self, obj)

#===============================================================================
# ResourceJSONRepresentation
#===============================================================================
class ResourceJSONRepresentation(object):
    '''Base class to extend when creating objects to be serialized as JSON
    for HTTP response bodies'''
    def __init__(self, object_type):
        self._object_type = object_type
        # Members to exclude when encoding
        self.exclude = ['exclude', 'as_json', 'is_http_error', 'get_localized']

    def as_json(self):
        return json.dumps(self, cls=ResourceJSONEncoder)

    @property
    def is_http_error(self):
        return False

    def get_localized(self, obj, field_name, language):
        if language != 'en':
            localized_field = ''.join([field_name, '_', language])
            if hasattr(obj, localized_field):
                return getattr(obj, localized_field)
        return getattr(obj, field_name)

