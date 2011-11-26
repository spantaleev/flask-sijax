# -*- coding: utf-8 -*-

from __future__ import with_statement
import unittest

import flask
import flask_sijax


def _assert_response_json(context, string):
    from sijax.helper import json
    try:
        obj = json.loads(string)
    except:
        context.fail('Cannot decode JSON!')
    else:
        context.assertTrue(isinstance(obj, list))
        for item in obj:
            context.assertTrue(isinstance(item, dict))
            context.assertTrue('type' in item)

class SijaxFlaskTestCase(unittest.TestCase):

    def test_route_always_adds_post_method(self):
        class FlaskMock(object):
            def __init__(self):
                self.methods = None

            def add_url_rule(self_mock, rule, view_func, endpoint, **options):
                self.assertEqual('/rule', rule)
                self_mock.methods = options.pop('methods', None)

        def try_route(methods_expected, **options):
            app = FlaskMock()
            decorator = flask_sijax.route(app, '/rule', **options)
            decorator(lambda a: a)
            self.assertEqual(tuple(methods_expected), app.methods)

        try_route(('GET', 'POST'))
        try_route(('GET', 'POST'), methods=('GET',))
        try_route(('POST', ), methods=())
        try_route(('GET', 'PUT', 'POST'), methods=('GET', 'PUT'))
        try_route(('GET', 'DELETE', 'POST'), methods=('GET', 'DELETE'))

    def test_sijax_helper_object_is_only_bound_to_g_in_a_request_context(self):
        app = flask.Flask(__name__)

        helper = flask_sijax.Sijax(app)

        with app.test_request_context():
            app.preprocess_request()
            self.assertEqual(id(helper), id(flask.g.sijax))

        # Make sure that access fails when outside of a request context
        try:
            flask.g.sijax
        except RuntimeError:
            # RuntimeError('working outside of request context')
            pass
        else:
            self.fail('Bound to g in a non-request context!')

    def test_delayed_app_initialization_works(self):
        # Makes sure that an app object can be provided at a later point
        # and that Sijax would still be registered correctly.
        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax()
        helper.init_app(app)
        with app.test_request_context():
            app.preprocess_request()
            self.assertEqual(id(helper), id(flask.g.sijax))

    def test_json_uri_config_is_used(self):
        uri = '/some/json_uri.here'

        app = flask.Flask(__name__)
        app.config['SIJAX_JSON_URI'] = uri
        helper = flask_sijax.Sijax(app)
        with app.test_request_context():
            app.preprocess_request()

            js = helper.get_js()
            self.assertTrue(uri in js)

    def test_request_uri_changing_works(self):
        # The request URI is automatically detected,
        # but could be changed to something else on each request
        # Changes should not be preserved throughout different requests though

        app = flask.Flask(__name__)

        helper = flask_sijax.Sijax(app)

        with app.test_request_context():
            app.preprocess_request()

            js = helper.get_js()
            self.assertTrue('Sijax.setRequestUri("/");' in js)

            helper.set_request_uri('http://something.else/')

            js = helper.get_js()
            self.assertFalse('Sijax.setRequestUri("/");' in js)
            self.assertTrue('Sijax.setRequestUri("http://something.else/");' in js)

        # Ensure that the changed request uri was valid for the previous request only
        with app.test_request_context():
            app.preprocess_request()

            js = helper.get_js()
            self.assertTrue('Sijax.setRequestUri("/");' in js)
            self.assertFalse('Sijax.setRequestUri("http://something.else/");' in js)

        # Test that a more complex request url (with query string, etc) works
        with app.test_request_context('/relative/url?query=string&is=here'):
            app.preprocess_request()

            js = helper.get_js()
            self.assertTrue('Sijax.setRequestUri("/relative/url?query=string&is=here");' in js)

    def test_registering_callbacks_in_a_non_request_context_fails(self):
        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax(app)

        try:
            helper.register_callback('test', lambda r: r)
            self.fail('Callback registered, but failure was expected!')
        except AttributeError:
            # helper._sijax (and flask.g.sijax)
            pass

    def test_registering_callbacks_in_a_request_context_with_no_preprocessing_fails(self):
        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax(app)

        with app.test_request_context():
            try:
                helper.register_callback('test', lambda r: r)
                self.fail('Callback registered, but failure was expected!')
            except AttributeError:
                # helper._sijax (and flask.g.sijax)
                pass

    def test_register_callback_works(self):
        call_history = []

        def callback(obj_response):
            call_history.append('callback')
            obj_response.alert('test')


        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax(app)

        with app.test_request_context():
            app.preprocess_request()

            helper.register_callback('test', callback)

            # no data, cannot determine request as a sijax request
            self.assertFalse(helper.is_sijax_request)

            cls_sijax = helper._sijax.__class__
            helper._sijax.set_data({cls_sijax.PARAM_REQUEST: 'test', cls_sijax.PARAM_ARGS: '[]'})

            self.assertTrue(helper.is_sijax_request)
            response = helper.process_request()
            self.assertEqual(['callback'], call_history)
            _assert_response_json(self, response)

    def test_upload_callbacks_receive_the_expected_arguments(self):
        # Upload callbacks should have the following signature:
        #   def function(obj_response, flask_request_files, form_values)
        # The extension should ensure that the proper arguments are passed
        import sijax
        from types import GeneratorType

        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax(app)

        call_history = []

        def callback(obj_response, files, form_values):
            call_history.append(form_values)
            call_history.append(id(files))

        with app.test_request_context():
            app.preprocess_request()

            helper.register_upload_callback('form_id', callback)
            func_name = sijax.plugin.upload.func_name_by_form_id('form_id')

            cls_sijax = helper._sijax.__class__

            post = {cls_sijax.PARAM_REQUEST: func_name, cls_sijax.PARAM_ARGS: '["form_id"]', 'post_key': 'val'}
            helper._sijax.set_data(post)
            self.assertTrue(helper.is_sijax_request)
            response = helper._sijax.process_request()
            self.assertTrue(isinstance(response, GeneratorType))
            for r in response: pass

            expected_history = [{'post_key': 'val'}, id(flask.request.files)]
            self.assertEqual(expected_history, call_history)

    def test_sijax_helper_passes_correct_post_data(self):
        # It's expected that the Sijax Helper class passes `flask.request.form`
        # as post data in the "on before request" stage
        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax(app)

        with app.test_request_context():
            app.preprocess_request()
            self.assertEqual(id(helper._sijax.get_data()), id(flask.request.form))

    def test_process_request_returns_a_string_or_a_flask_response_object(self):
        # flask_sijax.Sijax.process_request should return a string for regular functions
        # and a Flask.Response object for functions that use a generator (streaming functions)
        from sijax.response import StreamingIframeResponse

        app = flask.Flask(__name__)
        helper = flask_sijax.Sijax(app)

        with app.test_request_context():
            app.preprocess_request()

            cls_sijax = helper._sijax.__class__

            post = {cls_sijax.PARAM_REQUEST: 'callback', cls_sijax.PARAM_ARGS: '[]'}
            helper._sijax.set_data(post)
            helper.register_callback('callback', lambda r: r)
            response = helper.process_request()
            self.assertTrue(isinstance(response, type('string')))

            helper.register_callback('callback', lambda r: r, response_class=StreamingIframeResponse)
            response = helper.process_request()
            self.assertTrue(isinstance(response, flask.Response))

if __name__ == '__main__':
    unittest.main()
