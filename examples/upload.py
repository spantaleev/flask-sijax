# -*- coding: utf-8 -*-

"""Demonstration of the Sijax Upload plugin.

The Sijax Upload plugin allows you to easily transform any form
on your page into a "Sijax-enabled" form. Such forms will be submitted
using Sijax (ajax upload) and the upload will be handled by your Sijax handler
function in the same way regular Sijax handler functions are called.

"""

import os, sys

path = os.path.join('.', os.path.dirname(__file__), '../')
sys.path.append(path)

from flask import Flask, g, render_template
import flask_sijax

app = Flask(__name__)

# The path where you want the extension to create the needed javascript files
# DON'T put any of your files in this directory, because they'll be deleted!
app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

# You need to point Sijax to the json2.js library if you want to support
# browsers that don't support JSON natively (like IE <= 7)
app.config["SIJAX_JSON_URI"] = '/static/js/sijax/json2.js'

flask_sijax.Sijax(app)

class SijaxHandler(object):
    """A container class for all Sijax handlers.

    Grouping all Sijax handler functions in a class
    (or a Python module) allows them all to be registered with
    a single line of code.
    """

    @staticmethod
    def _dump_data(obj_response, files, form_values, container_id):
        def dump_files():
            if 'file' not in files:
                return 'Bad upload'

            file_data = files['file']
            file_name = file_data.filename
            if file_name is None:
                return 'Nothing uploaded'

            file_type = file_data.content_type
            file_size = len(file_data.read())
            return 'Uploaded file %s (%s) - %sB' % (file_name, file_type, file_size)

        html = """Form values: %s<hr />Files: %s"""
        html = html % (str(form_values), dump_files())

        obj_response.html('#%s' % container_id, html)

    @staticmethod
    def form_one_handler(obj_response, files, form_values):
        SijaxHandler._dump_data(obj_response, files, form_values, 'formOneResponse')

    @staticmethod
    def form_two_handler(obj_response, files, form_values):
        SijaxHandler._dump_data(obj_response, files, form_values, 'formTwoResponse')

        obj_response.reset_form()
        obj_response.html_append('#formTwoResponse', '<br />Form elements were reset!<br />Doing some more work (2 seconds)..')

        # Send the data to the browser now
        yield obj_response

        from time import sleep
        sleep(2)

        obj_response.html_append('#formTwoResponse', '<br />Finished!')


@flask_sijax.route(app, "/")
def index():
    # Notice how we're doing callback registration on each request,
    # instead of only when needed (when the request is a Sijax request).
    # This is because `register_upload_callback` returns some javascript
    # that prepares the form on the page.
    form_init_js = ''
    form_init_js += g.sijax.register_upload_callback('formOne', SijaxHandler.form_one_handler)
    form_init_js += g.sijax.register_upload_callback('formTwo', SijaxHandler.form_two_handler)

    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # The handlers are already registered above.. we can process the request
        return g.sijax.process_request()

    return render_template('upload.html', form_init_js=form_init_js)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
