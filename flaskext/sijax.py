# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import g, request, Response

import sijax

__version__ = '0.1.0'


class SijaxHelper(object):

    def __init__(self, app):
        self._app = app

        app.before_request(self._on_before_request)

        static_path = app.config.get('SIJAX_STATIC_PATH', None)
        if static_path is not None:
            sijax.helper.init_static_path(static_path)

        self._json_uri = app.config.get('SIJAX_JSON_URI', None)
        self._request_uri = None

        #: Reference to the underlying Sijax object
        self._sijax = None

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['sijax'] = self

    def set_request_uri(self, uri):
        """Changes the request URI from the automatically selected one.

        The automatically selected URI is the URI of the current request.
        You can override that with another URI (for this request only),
        by using this function.
        """
        self._sijax.set_request_uri(uri)

    def _on_before_request(self):
        g.sijax = self

        self._sijax = sijax.Sijax.Sijax()

        self._sijax.set_data(request.form)
        self._sijax.set_request_uri(request.url)

        if self._json_uri is not None:
            self._sijax.set_json_uri(self._json_uri)

    def register_callback(self, *args, **kwargs):
        """Registers a single callback function.

        Refer to :meth:`sijax.Sijax.Sijax.register_callback`
        for more details.
        """
        self._sijax.register_callback(*args, **kwargs)

    def register_object(self, *args, **kwargs):
        """Registers all functions from the object.

        This makes mass registration of functions a lot easier.

        Refer to :meth:`sijax.Sijax.Sijax.register_object`
        for more details.
        """
        self._sijax.register_object(*args, **kwargs)

    def register_comet_callback(self, *args, **kwargs):
        """Registers a single Comet callback function.

        Refer to :meth:`sijax.plugin.comet.register_comet_callback`
        for more details.
        """
        sijax.plugin.comet.register_comet_callback(self._sijax, *args, **kwargs)

    def register_comet_object(self, *args, **kwargs):
        """Registers all functions from the object as Comet functions.

        This makes mass registration of functions a lot easier.

        Refer to :meth:`sijax.plugin.comet.register_comet_object`
        for more details.
        """
        sijax.plugin.comet.register_comet_object(self._sijax, *args, **kwargs)

    def register_upload_callback(self, *args, **kwargs):
        """Registers an Upload function to handle a certain form.

        Refer to :meth:`sijax.plugin.upload.register_upload_callback`
        for more details.

        :return: string - javascript code that initializes the form
        """
        if 'args_extra' not in kwargs:
            kwargs['args_extra'] = [request.files]
        return sijax.plugin.upload.register_upload_callback(self._sijax, *args, **kwargs)
        
    def register_event(self, *args, **kwargs):
        """Registers a new event handler.

        Refer to :meth:`sijax.Sijax.Sijax.register_event`
        for more details.
        """
        self._sijax.register_event(*args, **kwargs)

    @property
    def is_sijax_request(self):
        """Tells whether the current request is meant to be handled by Sijax.

        Refer to :meth:`sijax.Sijax.Sijax.is_sijax_request` for more details.
        """
        return self._sijax.is_sijax_request()

    def process_request(self):
        """Processes the Sijax request and returns the proper response.

        Refer to :meth:`sijax.Sijax.Sijax.process_request` for more details.
        """


        response = self._sijax.process_request()
        return _make_response(response)

    def execute_callback(self, *args, **kwargs):
        """Executes a callback and returns the proper response.

        Refer to :meth:`sijax.Sijax.Sijax.execute_callback` for more details.
        """
        response = self._sijax.execute_callback(*args, **kwargs)
        return _make_response(response)

    def get_js(self):
        """Returns the javascript code that sets up the client for this request.

        This code is request-specific, be sure to put it on each page that needs
        to use Sijax.
        """
        return self._sijax.get_js()


def _make_response(response):
    """Takes a Sijax response object and returns a valid Flask response object."""

    from types import GeneratorType

    if isinstance(response, GeneratorType):                                              
        # Streaming response using a generator (non-JSON)
        return Response(response, direct_passthrough=True)                               
                                                                                         
    # Non-streaming response - a single JSON string 
    return response 
    

def init_sijax(app):
    return SijaxHelper(app)


def route(app_or_module_obj, rule, **options): 
    """A wrapper to app.route() or mod.route() that always adds the POST method
    to the allowed methods for a handler.

    We're doing this because Sijax uses POST for data passing, which means that
    every endpoint that wants Sijax support would have to accept POST requests.
    """
    def decorator(f):
        methods = options.pop('methods', ('GET', 'POST'))
        if 'POST' not in methods:
            methods = tuple(methods) + ('POST',)
        options['methods'] = methods
        
        app_or_module_obj.add_url_rule(rule, None, f, **options)
        return f
        
    return decorator

