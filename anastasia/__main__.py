# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import argparse
import sys

from werkzeug.serving import run_simple

from anastasia.config import get_config
from anastasia.webapp import create_app


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        metavar="FILE",
        default="anastasia.cfg",
        help="configuration filename (default: anastasia.cfg)"
    )
    args = parser.parse_args()

    # Read configuration
    config = {}
    try:
        config = get_config(args.config)
    except (IOError) as error:
        sys.exit(error)

    webapp = create_app(config)
    run_simple(
        config['host'],
        config['port'],
        webapp,
        use_reloader=True,
        use_debugger=True,
        use_evalex=True
    )


if __name__ == "__main__":
    main()
