"""
Flask-Sijax
===========

Flask-Sijax is an extension for the `Flask <http://flask.pocoo.org>`_ microframework,
to simplify Sijax (`PyPi <http://pypi.python.org/pypi/Sijax>`_, `GitHub <https://github.com/spantaleev/sijax-python>`_) setup and usage for Flask users.

Sijax is a Python/jQuery library that makes AJAX easy to use in web applications.

Links
-----

* `source <https://github.com/spantaleev/flask-sijax>`_
* `documentation <http://packages.python.org/Flask-Sijax>`_
* `development version
  <https://github.com/spantaleev/flask-sijax/zipball/master#egg=Flask-Sijax-dev>`_
* `Sijax source <https://github.com/spantaleev/sijax-python>`_
* `Sijax documentation <http://packages.python.org/Sijax/>`_
"""

from setuptools import setup

setup(
    name = "Flask-Sijax",
    version = '0.3.1',
    description = "An extension for the Flask microframework that adds Sijax support.",
    long_description = __doc__,
    author = "Slavi Pantaleev",
    author_email = "s.pantaleev@gmail.com",
    url = "https://github.com/spantaleev/flask-sijax",
    keywords = ["ajax", "jQuery", "flask"],
    platforms = "any",
    license = "BSD",
    py_modules = ['flask_sijax'],
    install_requires = ['Flask>=0.7.0', 'Sijax>=0.2.0'],
    test_suite = 'tests',
    zip_safe = False,
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
