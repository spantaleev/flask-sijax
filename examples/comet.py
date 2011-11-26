# -*- coding: utf-8 -*-

"""A demonstration of Comet streaming functionality using Sijax."""

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

def comet_do_work_handler(obj_response, sleep_time):
    import time

    for i in range(6):
        width = '%spx' % (i * 80)
        obj_response.css('#progress', 'width', width)
        obj_response.html('#progress', width)

        # Yielding tells Sijax to flush the data to the browser.
        # This only works for Streaming functions (Comet or Upload)
        # and would not work for normal Sijax functions
        yield obj_response

        if i != 5:
            time.sleep(sleep_time)


@flask_sijax.route(app, "/")
def index():
    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # Let's register the handlers and tell Sijax to process it
        g.sijax.register_comet_callback('do_work', comet_do_work_handler)
        return g.sijax.process_request()

    return render_template('comet.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
