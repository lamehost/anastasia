# MIT License
#
# Copyright (c) 2022, Marco Marzetti <marco@lamehost.it>
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
APIRouter dor API v3.0

This module provies `get_api` which is a FastAPI app factory that provide the
APIrouter that implements API v3.0
"""

import mimetypes
import os
import random
import string
from typing_extensions import TypedDict

from fastapi import APIRouter, File, HTTPException, Path, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import AnyHttpUrl, BaseModel, Field

# Input Validation
IMAGEHASH = Path(description="Image hash string", min_lentgh=1, max_length=64)


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
def random_string(length: int = 8) -> str:
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
    return "".join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


def get_api(folder: str, baseurl: str = "") -> APIRouter:
    """
    APIRouter factory for API v3.0

    Returns an APIRouter instance for API v3.0 to create, read and delete
    images via REST.
    The `folder` argument tells the functions where the image files are
    located.

    Arguments:
    ---------
    folder: str
      Folder where files are stored
    baseurl: str
      Base URL used to build the link to the image after upload. Empty string
      means "guess"

    Returns:
    --------
    APIRouter: APIRouter instance of API v3.0
    """
    api = APIRouter(prefix="/3", tags=["Images"])

    # All of the methods below inherit `folder` from here
    # Fix relative path
    if not os.path.isabs(folder):
        folder = os.path.join(os.getcwd(), folder)

    @api.get(
        "/image/{image_hash}",
        response_class=FileResponse,
        responses={
            200: {"description": "Image retunerd"},
            404: {"description": "Image does not exist"},
            503: {"description": "Transient error"},
        },
        description="Returns image identified by `image_hash`",
    )
    async def get_image(image_hash: str = IMAGEHASH) -> str:
        """
        Gets image by `image_hash`

        Returns the path to an image in the the `folder` folder whose name is
        `image_hash`.

        Arguments:
        ----------
        image_hash: str
          Image name

        Returns:
        --------
        str: Image file path
        """
        filename = os.path.join(folder, image_hash)
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail=f"Unable to find image: {image_hash}")

        return filename

    @api.post(
        "/upload",
        response_model=UploadImageSchema,
        responses={
            200: {"description": "Image created"},
            400: {"description": "Bad request"},
            503: {"description": "Transient error"},
        },
        description="Upload a new image",
    )
    async def upload_image(request: Request, image: UploadFile = File(...)) -> dict:
        """
        Upload Image.

        Receives the image, saves it and returns a dict with the metadata.
        The link that points back to the URL is either based on `baseurl` or
        guessed via url_for.

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
                status_code=400, detail=f"Unsupported content-type: {image.content_type}"
            )

        extension = mimetypes.guess_extension(image.content_type)
        image_hash = random_string(8) + f"{extension}"
        file_path = os.path.join(folder, image_hash)
        data = await image.read()

        if baseurl:
            url_path = api.url_path_for("get_image", **{"image_hash": image_hash})
            while url_path.startswith("/"):
                url_path = url_path[1:]
            link = f"{baseurl}{url_path}"
        else:
            link = request.url_for("get_image", **{"image_hash": image_hash})

        try:
            with open(file_path, "wb") as file:
                file.write(data)
        except FileNotFoundError as error:
            raise HTTPException(status_code=503, detail="Unable to upload the image") from error

        return {
            "data": {"deletehash": image_hash, "link": str(link)},
            "success": True,
            "status": 200,
        }

    @api.delete(
        "/image/{image_hash}",
        status_code=204,
        responses={
            204: {"description": "Image deleted"},
            404: {"description": "Not Found"},
            503: {"description": "Transient error"},
        },
        description="Deletes an existing image",
    )
    async def delete_image(image_hash: str = IMAGEHASH) -> None:
        """
        Deletes image by `image_hash`

        Delete from `folder` folder the image whose name is `image_hash`.

        Arguments:
        ----------
        image_hash: str
          Image name
        """

        filename = os.path.join(folder, image_hash)

        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Image does not exist")

        try:
            os.unlink(filename)
        except IOError as error:
            raise HTTPException(status_code=503, detail="Unable to delete the image") from error

    return api
