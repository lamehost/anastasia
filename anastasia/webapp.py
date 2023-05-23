# MIT License
#
# Copyright (c) 2023, Marco Marzetti <marco@lamehost.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
FastAPI app.

This module provies `create_app` which is a FastAPI app factory that provide
API and web frontend for the application.
"""

import os
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from anastasia.routers import v3_0
from anastasia.settings import Settings

VERSION = "1.0.3"


def create_app(api_mount_point: str = "/api/", settings: dict = False):
    """
    FastAPI app factory.

    Parses configuration from `anastasia.cfg` and returns a FastAPI instance
    that you can run via uvicorn.

    Parameters:
    ----------
    api_mount_point: str
        Path the API will be mounted on. (Default: '/api/')
    settings: dict
        App configuration settings. If False, get from configuration file.
        Default: False

    Returns:
    --------
    Fastapi: FastAPI app instance
    """
    # Read settings
    if not settings:
        settings = Settings().dict()

    # Create root webapp
    webapp = FastAPI(
        docs_url=False,
        contact={
            "name": settings["contact_name"],
            "url": settings["contact_url"],
            "email": settings["contact_email"],
        },
        title="Anastasia",
        description="VERY minimalist imgur-alike app",
        version=VERSION,
        openapi_url=False,
    )

    # Create API engine
    docs_url = "/docs" if settings["enable_docs"] else False

    api = FastAPI(
        docs_url=docs_url,
        contact={
            "name": settings["contact_name"],
            "url": settings["contact_url"],
            "email": settings["contact_email"],
        },
        title="Anastasia",
        description="VERY minimalist REST API that mimics some of imgur's methods.",  # pylint: disable=line-too-long # noqa
        version=VERSION,
        openapi_tags=[
            {
                "name": "Images",
                "description": "Add/Remove images",
                "externalDocs": {
                    "description": "README",
                    "url": "https://github.com/lamehost/anastasia/blob/master/README.md",  # pylint: disable=line-too-long # noqa
                },
            },
        ],
        servers=[
            {
                "url": "/api",
                "description": "VERY minimalist REST API that mimics some of imgur's methods.",  # pylint: disable=line-too-long # noqa
            }
        ],
        responses={401: {"description": "Unauthorized"}},
    )

    # Consruct baseurl
    baseurl = settings["baseurl"]
    if settings["baseurl"]:
        while baseurl.endswith("/"):
            baseurl = baseurl[:-1]
        baseurl = f"{baseurl}{api_mount_point}"
        if not baseurl.endswith("/"):
            baseurl = f"{baseurl}/"

    # Create folder
    Path(settings["folder"]).mkdir(parents=True, exist_ok=True)

    # Import API versions
    api.include_router(v3_0.get_api(settings["folder"], baseurl))

    # Add custom headers as recommended by
    # https://github.com/shieldfy/API-Security-Checklist#output
    @api.middleware("http")
    async def add_custom_headers(request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "deny"
        # Force restrictive content-security-policy for JSON content
        try:
            if response.headers["content-type"] == "application/json":
                response.headers["Content-Security-Policy"] = "default-src 'none'"
        except KeyError:
            pass
        return response

    # Add API engine to webapp
    webapp.mount(api_mount_point, api)

    if settings["enable_gui"]:
        # Add HTML frontend to webapp
        app_directory = os.path.dirname(os.path.realpath(__file__))
        if settings["dadjokes_gui"]:
            static_directory = os.path.join(app_directory, "templates", "dadjokes")
        else:
            static_directory = os.path.join(app_directory, "templates", "regular")
        webapp.mount("/", StaticFiles(directory=static_directory, html=True), name="templates")

    return webapp
