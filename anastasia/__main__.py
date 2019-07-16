from flask import request, url_for, send_file, Response, current_app
from flask_api import FlaskAPI
from flask_api.exceptions import APIException, AuthenticationFailed, NotFound, NotAuthenticated, ParseError

import random
import string
import os
import sys
import codecs
import magic
import mimetypes
import argparse

from anastasia.configuration import get_config


anastasia = FlaskAPI(__name__)


def random_string(length=8):
    """
    random_string(length)

    Returns random string of the given length.
    """
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase + string.digits
        ) for _ in range(length
    ))


class ServiceUnavailable(APIException):
    '''App exception object'''
    def __init__(self, detail):
        self.status_code = 503
        self.detail = detail

@anastasia.route("/1/image/<name>", methods=['GET', 'DELETE'])
@anastasia.route("/1/image", methods=['POST'], defaults={'name': None})
def image(name):
    if request.method == 'POST':
        # Authenticate Client-IDs
        try:
            key, value = [_.strip() for _ in request.headers.get('Authorization', '').split(' ')]
        except ValueError:
            key = False
            value = False

        if key != 'Client-ID':
            raise NotAuthenticated('You must provide a valid Client-ID')
        elif value not in anastasia.config['client_ids']:
            raise AuthenticationFailed('Unauthorized Client-ID: %s' % value)

        # Save file
        try:
            image = request.files['image']
        except IndexError:
            raise ParseError("No image found")
 
        extension = mimetypes.guess_extension(image.mimetype)
        name = ''.join([random_string(), extension])
        filename = os.path.join(anastasia.config['folder'], name)

        try:
            image.save(filename)
        except IOError:
            raise ServiceUnavailable('Unable to save image file')

        # Return result
        return {
            'data': {
                'deletehash': name,
                'link': url_for('image', name=name, _external=True)
            },
            "success": True,
            "status": 200
        }
    elif request.method == 'DELETE':
        filename = os.path.join(anastasia.config['folder'], name)
        if not os.path.isabs(filename):
            filename = os.path.join(os.getcwd(), filename)
        try:
            os.unlink(filename)
        except IOError:
            raise NotFound('Unable to delete the specified resource')

        return {
            "data"    : True,
            "status"  : 200,
            "success" : True
        }
    else:
        filename = os.path.join(anastasia.config['folder'], name)
        if not os.path.isabs(filename):
            filename = os.path.join(os.getcwd(), filename)

        mime = magic.Magic(mime=True)
        try:
            mimetype = mime.from_file(filename)
        except IOError:
            raise NotFound('Unable to find the requested resource')

        return send_file(filename, mimetype=mimetype)


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

    with anastasia.app_context():
        current_app.config['folder'] = config['folder']
        current_app.config['client_ids'] = config['client_ids']

    anastasia.run(
        debug=True,
        host=config['host'],
        port=config['port']
    )


if __name__ == "__main__":
    main()