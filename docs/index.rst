.. Flask-Sijax documentation master file, created by
   sphinx-quickstart on Sun Mar  6 02:01:07 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-Sijax
===========

:Author: Slavi Pantaleev<s.pantaleev_REMOVE@ME_gmail.com>
:Version: |release|
:Source: github.com_
:Bug tracker: `github.com/issues <https://github.com/spantaleev/flask-sijax/issues>`_

Flask-Sijax helps you add Sijax_ support to your Flask_ applications.

Sijax is a Python/jQuery_ library that makes AJAX easy to use in web applications.

.. _github.com: https://github.com/spantaleev/flask-sijax
.. _Flask: http://flask.pocoo.org/
.. _jQuery: http://jquery.com/
.. _Sijax: http://pypi.python.org/pypi/Sijax

Installing Flask-Sijax
----------------------

Flask-Sijax is available on PyPI_ and can be installed using **easy_install**::

    easy_install flask-sijax

or using **pip**::

    pip install flask-sijax


.. _PyPI: http://pypi.python.org/pypi/Flask-Sijax/

Setting it up
-------------

Here's an example of how Flask-Sijax is typically initialized and configured::

    import os
    from flask import Flask
    import flask_sijax

    path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

    app = Flask(__name__)
    app.config['SIJAX_STATIC_PATH'] = path
    app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
    flask_sijax.Sijax(app)


Configuration options
---------------------

**Flask-Sijax** is configured via the standard Flask config API.
Here are the available configuration options:

* **SIJAX_STATIC_PATH** - set this to the static path where you want the Sijax files to be located.

Flask-Sijax takes care of keeping the Sijax files up to date in this directory (even between version changes).
The specified directory needs to be dedicated for Sijax static files. You should not put anything else in it.


* **SIJAX_JSON_URI** - the URI to load the ``json2.js`` static file from (in case it's needed).

Sijax uses JSON to pass data between the browser and server. This means that browsers either need to support
JSON natively or get JSON support from the ``json2.js`` file. Such browsers include IE <= 7.
If you've set a URI to ``json2.js`` and Sijax detects that the browser needs to load it, it will do so on demand.
The URI could be relative or absolute.


Making your Flask functions Sijax-aware
----------------------------------------------

Registering view functions with Flask is usually done using ``@app.route`` or ``@blueprint.route``.
Functions registered that way cannot provide Sijax functionality, because they cannot be accessed
using a POST method by default (and Sijax uses POST requests).

To make a view function capable of handling Sijax requests,
make it accessible via POST using ``@app.route('/url', methods=['GET', 'POST'])``
or use the ``@flask_sijax.route`` helper decorator like this::

    # Initialization code for Flask and Flask-Sijax
    # See above..

    # Functions registered with @app.route CANNOT use Sijax
    @app.route('/')
    def index():
        return 'Index'

    # Functions registered with @flask_sijax.route can use Sijax
    @flask_sijax.route(app, '/hello')
    def hello():
        # Every Sijax handler function (like this one) receives at least
        # one parameter automatically, much like Python passes `self`
        # to object methods.
        # The `obj_response` parameter is the function's way of talking
        # back to the browser
        def say_hi(obj_response):
            obj_response.alert('Hi there!')

        if g.sijax.is_sijax_request:
            # Sijax request detected - let Sijax handle it
            g.register_callback('say_hi', say_hi)
            return g.sijax.process_request()

        # Regular (non-Sijax request) - render the page template
        return _render_template()

Let's assume ``_render_template()`` renders the following page::

    <html>
    <head>
    <script type="text/javascript"
        src="{ URI to jQuery - not included with this project }"></script>
    <script type="text/javascript"
        src="/static/js/sijax/sijax.js"></script>
    <script type="text/javascript">
        {{ g.sijax.get_js()|safe }}
    </script>
    </head>
    <body>
        <a href="javascript://" onclick="Sijax.request('say_hi');"></a>
    </body>
    </html>

Clicking on the link will fire a Sijax request (a special ``jQuery.ajax()`` request) to the server.

This request is detected on the server by ``g.sijax.is_sijax_request()``, in which case you let Sijax handle the request.

All functions registered using ``g.sijax.register_callback()`` (see :meth:`flask_sijax.Sijax.register_callback`) are exposed for calling from the browser.

Calling ``g.sijax.process_request()`` tells Sijax to execute the appropriate (previously registered) function and return the response to the browser.

To learn more on ``obj_response`` and what it provides, see :class:`sijax.response.BaseResponse`.


Setting up the client (browser)
-------------------------------

The browser needs to talk to the server and that's done using `jQuery`_ (``jQuery.ajax``) and the Sijax javascript files.
This means that you'll have to load those on each page that needs to use Sijax.

After both files are loaded, you can put the javascript init code (``g.sijax.get_js()``) somewhere on the page.
That code is page-specific and needs to be executed, after the ``sijax.js`` file has loaded.

Assuming you've used the above configuration here's the HTML markup you need to add to your template::

    <script type="text/javascript"
        src="{ URI to jQuery - not included with this project}"></script>
    <script type="text/javascript"
        src="/static/js/sijax/sijax.js"></script>
    <script type="text/javascript">
        {{ g.sijax.get_js()|safe }}
    </script>

You can then invoke a Sijax function using javascript like this::

    Sijax.request('function_name', ['argument 1', 150, 'argument 3']);

provided it has been defined and registered with Sijax::

    def function_name(obj_response, arg1, arg2, arg3):
        obj_response.alert('You called the function successfully!')

    g.sijax.register_callback('function_name', function_name)

To learn more on ``Sijax.request()`` see :ref:`Sijax:clientside-sijax-request`.

Learn more on how it all fits together from the **Examples**.


Examples
--------

We have provided complete examples which you can run directly from the source distribution (if you've installed the dependencies - Flask_ and Sijax_ - both available on PyPI).

* **Hello** - a Hello world project

 - `Hello Code <https://github.com/spantaleev/flask-sijax/blob/master/examples/hello.py>`_
 - `Hello Template (jinja2) <https://github.com/spantaleev/flask-sijax/blob/master/examples/templates/hello.html>`_


* **Chat** - a simple Chat/Shoutbox

 - `Chat Code <https://github.com/spantaleev/flask-sijax/blob/master/examples/chat.py>`_
 - `Chat Template (jinja2) <https://github.com/spantaleev/flask-sijax/blob/master/examples/templates/chat.html>`_


* **Comet** - a demonstration of the :ref:`Comet Plugin <sijax:comet-plugin>`

 - `Comet Code <https://github.com/spantaleev/flask-sijax/blob/master/examples/comet.py>`_
 - `Comet Template (jinja2) <https://github.com/spantaleev/flask-sijax/blob/master/examples/templates/comet.html>`_


* **Upload** - a demonstration of the :ref:`Upload Plugin <sijax:upload-plugin>`

 - `Upload Code <https://github.com/spantaleev/flask-sijax/blob/master/examples/upload.py>`_
 - `Upload Template (jinja2) <https://github.com/spantaleev/flask-sijax/blob/master/examples/templates/upload.html>`_


Sijax documentation
-------------------

The `documentation for Sijax <http://packages.python.org/Sijax/>`_ is very exhaustive and even though you're using the Flask-Sijax extension, which hides some of the details for you, you can still learn a lot from it.

* :ref:`Using Sijax <sijax:usage>`
* :ref:`Comet Plugin <sijax:comet-plugin>`
* :ref:`Upload Plugin <sijax:upload-plugin>`
* :ref:`Sijax.request() <sijax:clientside-sijax-request>`
* :ref:`Sijax.getFormValues() <sijax:clientside-sijax-get-form-values>`
* :ref:`FAQ <sijax:faq>`


API
---

.. autofunction:: flask_sijax.route
.. autoclass:: flask_sijax.Sijax
   :members:

