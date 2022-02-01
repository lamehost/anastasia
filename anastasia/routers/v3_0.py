"""
APIRouter dor API v3.0

This module provies `get_api` which is a FastAPI app factory that provide the APIrouter that
implements API v3.0
"""

import os
import mimetypes
import string
import random
from typing import TypedDict
from urllib.parse import urljoin

from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Request
from fastapi.responses import FileResponse

from pydantic import BaseModel, Field, AnyHttpUrl


# Input Validation
IMAGEHASH = Query(
    "",
    description="Image hash string",
    min_lentgh=1,
    max_length=64
)

# Response Schemas
class UploadImageDataFieldSchema(TypedDict, total=True):
    """Defines the `data` field of the `UploadImageSchema` schema"""
    deletehash: str = Field(min_length=1, max_length=64)
    link: AnyHttpUrl

class UploadImageSchema(BaseModel):
    """Schema for `upload_image` responses"""
    data: UploadImageDataFieldSchema = None
    success: bool = True
    status: int = 200


# Supporting methods
def random_string(length: int = 8):
    """
    Returns random string of the given length.

    Arguments:
    ----------
    length: int (optional)
      Defines the length of the string that will be returned (default: 8)

    Returns:
    --------
    str: Random string
    """
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase + string.digits
        ) for _ in range(length)
    )


def get_api(folder: str, baseurl: str = ""):
    """
    APIRouter factory for API v3.0

    Returns an APIRouter instance for API v3.0 to create, read and delete images via REST.
    The `folder` argument tells the functions where the image files are located.

    Arguments:
    ---------
    folder: str
      Folder where files are stored
    baseurl: str or bool
      Base URL used to build the link to the image after upload. Empty string means "guess"

    Returns:
    --------
    APIRouter: APIRouter instance of API v3.0
    """
    api = APIRouter(
        prefix="/3",
        tags=["Images"]
    )

    # All of the methods below inherit `folder` from here
    # Fix relative path
    if not os.path.isabs(folder):
        folder = os.path.join(os.getcwd(), folder)

    @api.get(
        "/image/{image_hash}",
        response_class=FileResponse,
        description="Returns image identified by `image_hash`"
    )
    async def get_image(image_hash: str = IMAGEHASH):
        """
        Gets image by `image_hash`

        Returns the path to an image in the the `folder` folder whose name is `image_hash`.

        Arguments:
        ----------
        image_hash: str
          Image name

        Returns:
        --------
        str: Image file path
        """
        return os.path.join(folder, image_hash)

    @api.post(
        "/upload",
        response_model=UploadImageSchema,
        responses={
            400: {"description": "Bad request"},
            503: {"description": "Transient error"}
        },
        description="Upload a new image",
    )
    async def upload_image(request: Request, image: UploadFile = File(...)):
        """
        Upload Image.

        Receives the image, saves it and returns a dict with the metadata.
        The link that points back to the URL is either based on `baseurl` or guessed via url_for.

        Arguments:
        ----------
        request: Request
          The HTTP request object
        image: UploadFile
          The image itself

        Returns:
        --------
        dict: Metadata that describe the image file (see UploadImageSchema).
        """
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported content-type: {image.content_type}"
            )

        extension = mimetypes.guess_extension(image.content_type)
        image_hash = random_string(8) + f"{extension}"
        file_path = os.path.join(folder, image_hash)
        data = await image.read()

        if baseurl:
            url_path = api.url_path_for("get_image", **{"image_hash": image_hash})
            link = urljoin(baseurl, url_path)
        else:
            link = request.url_for("get_image", **{"image_hash": image_hash})

        try:
            with open(file_path, "wb") as file:
                file.write(data)
        except FileNotFoundError as error:
            print(error)
            raise HTTPException(status_code=503, detail='Unable to upload the image') from error

        return {
            "data": {
                "deletehash": image_hash,
                "link": link
            },
            "success": True,
            "status": 200
        }

    @api.delete(
        "/image/{image_hash}",
        status_code=204,
        responses={
            404: {"description": "Not Found"},
            503: {"description": "Transient error"}
        },
        description="Deletes an existing image",
    )
    async def delete_image(image_hash: str = IMAGEHASH):
        """
        Deletes image by `image_hash`

        Delete from `folder` folder the image whose name is `image_hash`.

        Arguments:
        ----------
        image_hash: str
          Image name
        """

        file_path = os.path.join(folder, image_hash)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail='Image does not exist')

        try:
            os.unlink(file_path)
        except IOError as error:
            raise HTTPException(status_code=503, detail='Unable to delete the image') from error


    return api
