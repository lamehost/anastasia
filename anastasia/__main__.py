# MIT License
#
# Copyright (c) 2024, Marco Marzetti <marco@lamehost.it>
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

"""Main entrypoint for the package"""

import os

import uvicorn


def main() -> None:
    """
    Main package function.

    Starts uvicorn and runs `anastasia.create_app()`
    """

    # Import config from ENV
    host = os.getenv("ANASTASIA_HOST", "0.0.0.0")
    port = int(os.getenv("ANASTASIA_PORT", "8080"))
    debug = os.getenv("ANASTASIA_DEBUG", None) is not None

    if debug:
        reload = True
        log_level = "debug"
    else:
        reload = False
        log_level = "debug"

    # Launch webapp through uvicorn
    uvicorn.run(
        "anastasia:create_app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
        factory=True,
        server_header=False,
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
