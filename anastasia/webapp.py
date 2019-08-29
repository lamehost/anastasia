# -*- coding: utf-8 -*-

from __future__ import absolute_import

import mimetypes
import os
import random
import string

from flask import Flask, abort, request, send_file, url_for
from flask_restful import Api, Resource


def random_string(length=8):
    """
    random_string(length)
    Returns random string of the given length.
    """
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase + string.digits
        ) for _ in range(length)
    )

def create_app(config=None):
    app = Flask(__name__)
    api = Api(app)

    config = config or {}
    if config:
        with app.app_context():
            for key, value in config.items():
                app.config[key] = value

    try:
        api.debug = config['debug']
    except KeyError:
        pass

    class NewImage(Resource):
        def post(self):
            try:
                key, value = [
                    _.strip() for _ in request.headers.get('Authorization', '').split(' ')
                ]
            except ValueError:
                key = False
                value = False

            if key != 'Client-ID':
                abort(401, 'You must provide a valid Client-ID')
            elif value not in app.config['client_ids']:
                abort(401, 'Unauthorized Client-ID: %s' % value)

            # Save file
            try:
                image = request.files['image']
            except IndexError:
                abort(400, "No image was sent")

            extension = mimetypes.guess_extension(image.mimetype)
            name = ''.join([random_string(), extension])
            filename = os.path.join(app.config['folder'], name)

            try:
                image.save(filename)
            except IOError:
                abort(503, 'Unable to save image file')

            # Return result
            return {
                'data': {
                    'deletehash': name,
                    'link': url_for('existingimage', name=name, _external=True)
                },
                "success": True,
                "status": 200
            }

    class ExistingImage(Resource):
        def delete(self, name):
            filename = os.path.join(app.config['folder'], name)
            if not os.path.isabs(filename):
                filename = os.path.join(os.getcwd(), filename)

            if not os.path.exists(filename):
                raise abort(404, 'Image does not exist')

            try:
                os.unlink(filename)
            except IOError:
                raise abort(503, 'Unable to delete the image')

            return {
                "data"    : True,
                "status"  : 200,
                "success" : True
            }
        def get(self, name):
            filename = os.path.join(app.config['folder'], name)
            if not os.path.isabs(filename):
                filename = os.path.join(os.getcwd(), filename)

            # To explicitely set mimetype=None tells send_file to guess the type on its own
            return send_file(filename, mimetype=None)

    api.add_resource(NewImage, "/1/image", "/1/image/")
    api.add_resource(ExistingImage, "/1/image/<string:name>")

    return app
