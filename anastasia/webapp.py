"""
FastAPI app.

This module provies `create_app` which is a FastAPI app factory that provide API and web frontends
for the application.
"""

import os
from typing import Callable

from fastapi import FastAPI, Request #, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings, EmailStr

from anastasia.routers import v3_0
from anastasia.__about__ import __version__

class Settings(BaseSettings):
    """App configuration schema"""
    client_ids: str
    folder: str
    contact_name: str
    contact_url: str
    contact_email: EmailStr

    class Config:
        """Tells pydantic to import ENV from `anastasia.cfg`"""
        env_file = os.getenv('CANDELA_ENV', 'anastasia.cfg')
        env_file_encoding = 'utf-8'

def create_app():
    """
    FastAPI app factory.

    Parses configuration from `anastasia.cfg` and returns a FastAPI instance that you can run
    via uvicorn.

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
        description="VERY minimalistic imgur-alike app",
        version=__version__,
        openapi_url=False
    )

    # Create API engine
    api = FastAPI(
        docs_url='/docs',
        contact={
            "name": settings.contact_name,
            "url": settings.contact_url,
            "email": settings.contact_email
        },
        title="Anastasia",
        description="VERY minimalistic REST API that mimics some of imgur's methods.",
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
                "description": "VERY minimalistic REST API that mimics some of imgur's methods."
            }
        ],
        responses={
            401: {"description": "Unauthorized"}
        }
    )

    # Import API versions
    api.include_router(
        v3_0.get_api(settings.folder)
    )

    # # Auth layer
    # client_ids = [client_id.strip() for client_id in settings.client_ids.split(',')]
    # @api.middleware("http")
    # async def auth_layer(request: Request, call_next: Callable):
    #     try:
    #         key, client_id = request.headers['authorization'].split(" ", 2)
    #         assert key == "Client-ID"
    #     except KeyError as error:
    #         raise HTTPException(
    #             status_code=401,
    #             detail="Authorization header missing"
    #         ) from error
    #     except (ValueError, AssertionError) as error:
    #         raise HTTPException(
    #             status_code=401,
    #             detail="Authorization header malformed"
    #         ) from error
    #
    #     if client_id not in client_ids:
    #         raise HTTPException(
    #             status_code=401,
    #             detail="Unauthorized client id"
    #         )
    #
    #     response = await call_next(request)
    #     return response


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
    webapp.mount('/api/', api)

    # Add HTML frontend to webapp
    app_directory = os.path.dirname(os.path.realpath(__file__))
    static_directory = os.path.join(app_directory, 'templates')
    webapp.mount("/", StaticFiles(directory=static_directory, html = True), name="templates")

    return webapp
