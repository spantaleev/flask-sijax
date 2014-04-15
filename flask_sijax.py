# -*- coding: utf-8 -*-

from __future__ import absolute_import

from werkzeug.wsgi import ClosingIterator

from flask import g, request, Response, _request_ctx_stack

import sijax

class Sijax(object):
    """Helper class that you'll use to interact with Sijax.

    This class tries to look like :class:`sijax.Sijax`,
    although the API differs slightly in order to make things easier for you.
    """

    def __init__(self, app=None):
        self._request_uri = None

        #: Reference to the underlying :class:`sijax.Sijax` object
        self._sijax = None

        #: The URI to json2.js (JSON support for browsers without native one)
        self._json_uri = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._on_before_request)

        static_path = app.config.get('SIJAX_STATIC_PATH', None)
        if static_path is not None:
            sijax.helper.init_static_path(static_path)

        self._json_uri = app.config.get('SIJAX_JSON_URI', None)

        app.extensions = getattr(app, 'extensions', {})
        app.extensions['sijax'] = self

    def _on_before_request(self):
        g.sijax = self

        self._sijax = sijax.Sijax()
        self._sijax.set_data(request.form)

        url_relative = request.url[len(request.host_url) - 1:]
        self._sijax.set_request_uri(url_relative)

        if self._json_uri is not None:
            self._sijax.set_json_uri(self._json_uri)

    def set_request_uri(self, uri):
        """Changes the request URI from the automatically detected one.

        The automatically detected URI is the relative URI of the
        current request, as detected by Flask/Werkzeug.

        You can override the detected URI with another one
        (for the current request only), by using this function.
        """
        self._sijax.set_request_uri(uri)

    def register_callback(self, *args, **kwargs):
        """Registers a single callback function.

        Refer to :meth:`sijax.Sijax.register_callback`
        for more details - this is a direct proxy to it.
        """
        self._sijax.register_callback(*args, **kwargs)

    def register_object(self, *args, **kwargs):
        """Registers all "public" callable attributes of the given object.

        The object could be anything (module, class, class instance, etc.)

        This makes mass registration of functions a lot easier.

        Refer to :meth:`sijax.Sijax.register_object`
        for more details - this is a direct proxy to it.
        """
        self._sijax.register_object(*args, **kwargs)

    def register_comet_callback(self, *args, **kwargs):
        """Registers a single Comet callback function
        (see :ref:`comet-plugin`).

        Refer to :func:`sijax.plugin.comet.register_comet_callback`
        for more details - its signature differs slightly.

        This method's signature is the same, except that the first
        argument that :func:`sijax.plugin.comet.register_comet_callback`
        expects is the Sijax instance, and this method
        does that automatically, so you don't have to do it.
        """
        sijax.plugin.comet.register_comet_callback(self._sijax, *args, **kwargs)

    def register_comet_object(self, *args, **kwargs):
        """Registers all functions from the object as Comet functions
        (see :ref:`comet-plugin`).

        This makes mass registration of functions a lot easier.

        Refer to :func:`sijax.plugin.comet.register_comet_object`
        for more details -ts signature differs slightly.

        This method's signature is the same, except that the first
        argument that :func:`sijax.plugin.comet.register_comet_object`
        expects is the Sijax instance, and this method
        does that automatically, so you don't have to do it.
        """
        sijax.plugin.comet.register_comet_object(self._sijax, *args, **kwargs)

    def register_upload_callback(self, *args, **kwargs):
        """Registers an Upload function (see :ref:`upload-plugin`)
        to handle a certain form.

        Refer to :func:`sijax.plugin.upload.register_upload_callback`
        for more details.

        This method passes some additional arguments to your handler
        functions - the ``flask.request.files`` object.

        Your upload handler function's signature should look like this::

            def func(obj_response, files, form_values)

        :return: string - javascript code that initializes the form
        """
        if 'args_extra' not in kwargs:
            kwargs['args_extra'] = [request.files]
        return sijax.plugin.upload.register_upload_callback(self._sijax, *args, **kwargs)

    def register_event(self, *args, **kwargs):
        """Registers a new event handler.

        Refer to :meth:`sijax.Sijax.register_event`
        for more details - this is a direct proxy to it.
        """
        self._sijax.register_event(*args, **kwargs)

    @property
    def is_sijax_request(self):
        """Tells whether the current request is meant to be handled by Sijax.

        Refer to :attr:`sijax.Sijax.is_sijax_request` for more details -
        this is a direct proxy to it.
        """
        return self._sijax.is_sijax_request

    def process_request(self):
        """Processes the Sijax request and returns the proper response.

        Refer to :meth:`sijax.Sijax.process_request` for more details.
        """
        response = self._sijax.process_request()
        return _make_response(response)

    def execute_callback(self, *args, **kwargs):
        """Executes a callback and returns the proper response.

        Refer to :meth:`sijax.Sijax.execute_callback` for more details.
        """
        response = self._sijax.execute_callback(*args, **kwargs)
        return _make_response(response)

    def get_js(self):
        """Returns the javascript code that sets up the client for this request.

        This code is request-specific, be sure to put it on each page that needs
        to use Sijax.
        """
        return self._sijax.get_js()


def route(app_or_blueprint, rule, **options):
    """An alternative to :meth:`flask.Flask.route` or :meth:`flask.Blueprint.route` that
    always adds the ``POST`` method to the allowed endpoint request methods.

    You should use this for all your view functions that would need to use Sijax.

    We're doing this because Sijax uses ``POST`` for data passing,
    which means that every endpoint that wants Sijax support
    would have to accept ``POST`` requests.

    Registering functions that would use Sijax should happen like this::

        @flask_sijax.route(app, '/')
        def index():
            pass

    If you remember to make your view functions accessible via POST
    like this, you can avoid using this decorator::

        @app.route('/', methods=['GET', 'POST'])
        def index():
            pass
    """
    def decorator(f):
        methods = options.pop('methods', ('GET', 'POST'))
        if 'POST' not in methods:
            methods = tuple(methods) + ('POST',)
        options['methods'] = methods
        app_or_blueprint.add_url_rule(rule, None, f, **options)
        return f
    return decorator


def _make_response(sijax_response):
    """Takes a Sijax response object and returns a
    valid Flask response object."""
    from types import GeneratorType

    if isinstance(sijax_response, GeneratorType):
        # Streaming response using a generator (non-JSON response).
        # Upon returning a response, Flask would automatically destroy
        # the request data and uploaded files - done by `flask.ctx.RequestContext.auto_pop()`
        # We can't allow that, since the user-provided callback we're executing
        # from within the generator may want to access request data/files.
        # That's why we'll tell Flask to preserve the context and we'll clean up ourselves.

        request.environ['flask._preserve_context'] = True

        # Clean-up code taken from `flask.testing.TestingClient`
        def clean_up_context():
            top = _request_ctx_stack.top
            if top is not None and top.preserved:
                top.pop()

        # As per the WSGI specification, `close()` would be called on iterator responses.
        # Let's wrap the iterator in another one, which will forward that `close()` call to our clean-up callback.
        response = Response(ClosingIterator(sijax_response, clean_up_context), direct_passthrough=True)
    else:
        # Non-streaming response - a single JSON string
        response = Response(sijax_response)

    return response
