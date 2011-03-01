"""
Flask-Sijax
===========

Flask-Sijax is an extension for the `Flask <http://flask.pocoo.org>`_ microframework,
to simplify Sijax (`PyPi <http://pypi.python.org/pypi/Sijax>`_, `GitHub <https://github.com/spantaleev/sijax-python>`_) setup and usage for Flask users.
"""

from setuptools import setup

from flaskext.sijax import __version__

setup(
    name = "Flask-Sijax",
    version = __version__,
    description = "An extension for the Flask microframework that adds Sijax support.",
    long_description = __doc__,
    author = "Slavi Pantaleev",
    author_email = "s.pantaleev@gmail.com",
    url = "https://github.com/spantaleev/flask-sijax",
    keywords = ["ajax", "jQuery", "flask"],
    platforms = "any",
    license = "BSD",
    packages = ['flaskext'],
    namespace_packages=['flaskext'],
    install_requires = ['Flask', 'Sijax>=0.1.5'],
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
