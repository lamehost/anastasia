"""Main entrypoint for the package"""

import os
import uvicorn


def main():
    """
    Main package function.

    Starts uvicorn and runs `anastasia.create_app()`
    """

    # Import config from ENV
    host = os.getenv('ANASTASIA_HOST', '0.0.0.0')
    port = int(os.getenv('ANASTASIA_PORT', '8080'))
    debug = os.getenv('ANASTASIA_DEBUG', None) is not None

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
        proxy_headers=True
    )


if __name__ == "__main__":
    main()
