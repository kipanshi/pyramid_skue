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

# ***** Python built-in modules *****
import urllib

__author__ = "Greivin Lopez"
__copyright__ = u"Copyright 2012, The Skuë Project"
__credits__ = ["Greivin Lopez"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Greivin Lopez"
__email__ = "greivin.lopez@gmail.com"
__status__ = "Development"


#===============================================================================
# parse_body
#===============================================================================
def parse_body(body):
    """Parses the given body from an HTTP request to retrieve arguments

    Args
      body: The body of the request. E.g. 'name=value&name2=value2'

    Returns:
      A dictionary with all the parameters extracted from the provided
      value. E.g. { 'name':'value', 'name2':'value2' }

    Note: All argument values will be strings.
    """
    output = {}
    if len(body) > 0:
        parameters = body.split('&')
        for parameter in parameters:
            parsed = parameter.split('=')
            if len(parsed) > 1:
                output[parsed[0]] = urllib.unquote_plus(parsed[1])
    return output

#===============================================================================
# restify
#===============================================================================
def restify(text):
    """Transform the given text to something that could be use as a section
    of a REST URI.

    Replaces white spaces with hyphens.

    Args:
      text: The text to be converted.

    Returns:
      A string value equivalent to the given text but suited for a REST URI.
    """
    text = text.replace(' ', '-').lower()
    return ''.join(char for char in text if char.isalnum() or char == '-')
