#!/usr/bin/env python
#
# Copyright 2012 Martin J Chorley
# Adapted from code written by Martin J Chorley & Matthew J Williams

import time
import json
import urllib
import urllib2
import copy
import threading
import hashlib

class APIWrapper:

    def __init__( self, session_token, api_key, api_secret ):

        self.session_token = session_token
        self.api_key = api_key
        self.api_secret = api_secret

        scheme = 'http://'
        netloc = 'ws.audioscrobbler.com'
        path_prefix = '/2.0'

        self.api_base_url = scheme + netloc + path_prefix

        queries_per_second = 5
        query_interval = 1 / float( queries_per_second )
        
        rate_monitor = { 'wait' : query_interval,
                                'earliest' : None,
                                'timer' : None }

        self.__rate_controller( rate_monitor )

    def __rate_controller( self, monitor_dict ):
        if monitor_dict['timer'] is not None:
            monitor_dict['timer'].join()

            while time.time() < monitor_dict['earliest']:
                time.sleep( monitor_dict['earliest'] - time.time() )

        earliest = time.time() + monitor_dict['wait']
        timer = threading.Timer( earliest-time.time(), lambda: None )
        monitor_dict['earliest'] = earliest
        monitor_dict['timer'] = timer
        monitor_dict['timer'].start()

    def query( self, method, get_params, authenticated=True, post=False ):
        params = copy.copy( get_params )

        for field in ['session_token', 'api_key']:
            if field in params:
                del params[field]

        params['api_key'] = self.api_key
        params['method'] = method
        
        if authenticated:
            params['sk'] = self.session_token
            params = self.__sign_request( params )

        params['format'] = 'json'

        data = urllib.urlencode( params )

        if post:
            url = self.api_base_url
            url = urllib2.Request( url, data )
        else:
            url = self.api_base_url + '/?' + data
            url = urllib2.Request( url )

        try:
            response = urllib2.urlopen( url )
        except urllib2.HttpError as e:
            raise e
        except urllib2.URLError as e:
            raise e

        raw_data = response.read( )
        py_data = json.loads( raw_data )

        error_code = py_data.get('error', None)
        if error_code is not None:
            error_message = py_data['message']
            raise LastFMRequestError( error_code, error_message )

        return py_data

    def __sign_request( self, params ):
        signature = ''
        for key in sorted( params.iterkeys( ) ):
            signature = '%s%s%s' % ( signature, key, params[key] )

        signature = '%s%s' % ( signature, self.api_secret )
        signature = hashlib.md5( signature ).hexdigest( )
        params['api_sig'] = signature

        return params

class LastFMRequestError( RuntimeError ):
    def __init__( self, error_code, error_message ):
        self.error_code = error_code
        self.error_message = error_message

    def __str__( self ):
        return '%s:%s' % ( self.error_code, self.error_message )

