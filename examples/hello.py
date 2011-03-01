# -*- coding: utf-8 -*-

"""A very simple example demonstrating Sijax and the Flask-Sijax extension."""

import os, sys

path = os.path.join('.', os.path.dirname(__file__), '../')
sys.path.append(path)


from flask import Flask, g, render_template, Markup
from flaskext.sijax import init_sijax, route

app = Flask(__name__)

# The path where you want the extension to create the needed javascript files
# DON'T put any of your files in this directory, because they'll be deleted!
app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

# You need to point Sijax to the json2.js library if you want to support
# browsers that don't support JSON natively (like IE <= 7)
app.config["SIJAX_JSON_URI"] = '/static/js/sijax/json2.js'

init_sijax(app)

# Regular flask view function - Sijax is unavailable here
@app.route("/")
def hello():
    return "Hello World!<br /><a href='/sijax'>Go to Sijax test</a>"

# Sijax enabled function - notice the `@route` decorator
# in place of `@app.route` (above) or `@mod.route` (when using Modules)
@route(app, "/sijax")
def hello_sijax():
    # Sijax handler function receiving 2 arguments from the browser
    # The first argument (obj_response) is passed automatically
    # by Sijax (much like Python passes `self` to object methods)
    def hello_handler(obj_response, hello_from, hello_to):
        obj_response.alert('Hello from %s to %s' % (hello_from, hello_to))
        obj_response.css('a', 'color', 'green')

    # Another Sijax handler function which receives no arguments
    def goodbye_handler(obj_response):
        obj_response.alert('Goodbye, whoever you are.')
        obj_response.css('a', 'color', 'red')

    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # Let's register the handlers and tell Sijax to process it
        g.sijax.register_callback('say_hello', hello_handler)
        g.sijax.register_callback('say_goodbye', goodbye_handler)
        return g.sijax.process_request()

    sijax_js = Markup(g.sijax.get_js())

    return render_template('hello.html', sijax_js=sijax_js)

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
