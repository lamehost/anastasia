"""
FastAPI app.

This module provies `create_app` which is a FastAPI app factory that provide API and web frontends
for the application.
"""

#
# Models lack the minimum amount of public methods
# Also pydantic very often raises no-name-in-module
#
# pylint: disable=too-few-public-methods, no-name-in-module


import os
from typing import Callable
from pathlib import Path

from fastapi import FastAPI, Request #, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings, EmailStr

from anastasia.routers import v3_0
from anastasia.__about__ import __version__

class Settings(BaseSettings):
    """App configuration schema"""
    # Image folder
    folder: str

    # API frontend stuff
    contact_name: str
    contact_url: str
    contact_email: EmailStr

    # Activate GUI
    enable_gui: bool = False

    # Activate API docs
    enable_docs: bool = False

    # Base URL for response
    baseurl: str = ""

    class Config:
        """Tells pydantic to import ENV from `anastasia.cfg`"""
        env_file = os.getenv('ANASTASIA_ENV', 'anastasia.cfg')
        env_file_encoding = 'utf-8'

def create_app(api_mount_point: str ='/api/'):
    """
    FastAPI app factory.

    Parses configuration from `anastasia.cfg` and returns a FastAPI instance that you can run
    via uvicorn.

    Parameters:
    ----------
    api_mount_point: str
     Path the API will be mounted on. (Default: '/api/')

    Returns:
    --------
    Fastapi: FastAPI app instance
    """
    # Read settings
    settings = Settings()

    # Create root webapp
    webapp = FastAPI(
        docs_url=False,
        contact={
            "name": settings.contact_name,
            "url": settings.contact_url,
            "email": settings.contact_email
        },
        title="Anastasia",
        description="VERY minimalist imgur-alike app",
        version=__version__,
        openapi_url=False
    )

    # Create API engine
    docs_url = '/docs' if settings.enable_docs else False

    api = FastAPI(
        docs_url=docs_url,
        contact={
            "name": settings.contact_name,
            "url": settings.contact_url,
            "email": settings.contact_email
        },
        title="Anastasia",
        description="VERY minimalist REST API that mimics some of imgur's methods.",
        version=__version__,
        openapi_tags=[
            {
                "name": "Images",
                "description": "Add/Remove images",
                "externalDocs": {
                    "description": "README",
                    "url": "https://github.com/lamehost/anastasia/blob/master/README.md",
                },
            },
        ],
        servers=[
            {
                "url": "/api",
                "description": "VERY minimalist REST API that mimics some of imgur's methods."
            }
        ],
        responses={
            401: {"description": "Unauthorized"}
        }
    )

    # Consruct baseurl
    baseurl = settings.baseurl
    if settings.baseurl:
        while baseurl.endswith('/'):
            baseurl = baseurl[:-1]
        baseurl = f"{baseurl}{api_mount_point}"
        if not baseurl.endswith('/'):
            baseurl = f"{baseurl}/"

    # Create folder
    Path(settings.folder).mkdir(parents=True, exist_ok=True)

    # Import API versions
    api.include_router(
        v3_0.get_api(settings.folder, baseurl)
    )

    # Add custom headers as recommended by https://github.com/shieldfy/API-Security-Checklist#output
    @api.middleware("http")
    async def add_custom_headers(request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "deny"
        # Force restrictive content-security-policy for JSON content
        try:
            if response.headers['content-type'] == 'application/json':
                response.headers["Content-Security-Policy"] = "default-src 'none'"
        except KeyError:
            pass
        return response

    # Add API engine to webapp
    webapp.mount(api_mount_point, api)

    if settings.enable_gui:
        # Add HTML frontend to webapp
        app_directory = os.path.dirname(os.path.realpath(__file__))
        static_directory = os.path.join(app_directory, 'templates')
        webapp.mount("/", StaticFiles(directory=static_directory, html = True), name="templates")

    return webapp
