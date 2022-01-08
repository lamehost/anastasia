"""
VERY minimalistic imgur-alike app.

Anastasia is a *VERY* minimalistic image upload app that implements some of imgur APIs.
It offers REST APIs and a simple web interface where you can drag and drop image file for instant
upload.
"""

from .webapp import create_app
from . import routers
