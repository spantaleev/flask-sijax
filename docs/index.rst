Flask-Sijax
===========

**Flask-Sijax** is an extension for the `Flask`_ microframework that adds `Sijax`_ support.

`Sijax`_ is a Python/`jQuery`_ library that makes AJAX easy and pleasant to use in your web applications.


Installing Flask-Sijax
----------------------

You can install using **pip** or **easy_install**::

    pip install Flask-Sijax

    # or

    easy_install Flask-Sijax


Configuring Flask-Sijax
-----------------------

**Flask-Sijax** is configured via the standard Flask config API.
Here are the available configuration options:

* **SIJAX_STATIC_PATH** - set this to the static path where you want the Sijax files to be located.

Flask-Sijax takes care of keeping the Sijax files up to date in this directory (even between version changes).
The specified directory needs to be dedicated for Sijax static files. You should not put anything else in it.


* **SIJAX_JSON_URI** - the URI to load the `json2.js` static file from (in case it's needed).

Sijax uses JSON to pass data between the browser and server. This means that browsers either need to support
JSON natively, or get JSON support from the `json2.js` file. Such browsers include IE <= 7.
If you've set a URI to `json2.js` and Sijax detects that the browser needs to load it, it will do so on demand.
The URI could be relative or absolute.

Here's an example of how Flask-Sijax is typically initted and configured::

    import os
    from flask import Flask
    from flaskext.sijax import init_sijax, route

    app = Flask(__name__)
    app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
    app.config["SIJAX_JSON_URI"] = '/static/js/sijax/json2.js'
    init_sijax(app)


Making your Flask (view) functions Sijax-aware
----------------------------------------------

To make a function support Sijax requests, you need to create the route to it in a special way.
If you're not new to Flask you're aware of the `@app.route` or `@mod.route` decorators that register
your function with Flask.

You need to use `@flaskext.sijax.route` instead of `@app.route` or `@mod.route` if you intend to use Sijax
within a given Flask endpoint function.
Here's how you do it::

    from flaskext.sijax import route

    # Instead of `@app.route` - the function below can use Sijax
    @route(app, '/hello')
    def hello():
        pass

    # Instead of `@mod.route` - the function below can use Sijax
    @route(mod, '/something')
    def something():
        pass


Setting up the client (browser)
-------------------------------

The browser needs to talk to the server and that's done using `jQuery`_ (`jQuery.ajax`) and the Sijax javascript files.
This means that you'll want to load those on each page that needs to use Sijax.

After both files are loaded, you can put the javascript init code (`g.sijax.get_js()`) somewhere on the page.
That code is page-specific and needs to be executed, after the `sijax.js` file has loaded.

Assuming you've used the above configuration here's what HTML markup you need to add to your template::

    <script type="text/javascript" src="{ URI to jQuery - not included with this project}"></script>
    <script type="text/javascript" src="/static/js/sijax/sijax.js"></script>
    <script type="text/javascript">
        { the result of `g.sijax.get_js()` here }
    </script>

You can then invoke Sijax functions like this::

    Sijax.request('function_name', ['argument 1', 150, 'argument 3', 'argument 4']);


More information
----------------

The above is only a brief introduction to Sijax and Flask-Sijax.
Take a look at the `examples` directory for some real examples
using Flask-Sijax and Flask.

If you really want to dig in, there's a lot more information in the `Sijax docs`_.


.. _Flask: http://flask.pocoo.org/
.. _jQuery: http://jquery.com/
.. _Sijax: http://pypi.python.org/pypi/Sijax
.. _Sijax docs: https://github.com/spantaleev/sijax-python/tree/master/docs
