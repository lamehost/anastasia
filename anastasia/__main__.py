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
    port = int(os.getenv('ANASTASIA_PORT', '8000'))
    debug = os.getenv('ANASTASIA_DEBUG', None) is not None

    # Launch webapp through uvicorn
    uvicorn.run(
        "anastasia:create_app",
        host=host,
        port=port,
        log_level=debug,
        reload=True,
        factory=True,
        server_header=False
    )


if __name__ == "__main__":
    main()
