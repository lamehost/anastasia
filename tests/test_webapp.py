import unittest
import os
import tempfile
from shutil import rmtree

from httpx import AsyncClient

from anastasia import create_app


class TestWebApp(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings = {
            # Image folder
            "folder": tempfile.mkdtemp(),
            # API frontend stuff
            "contact_name": "Average Joe",
            "contact_url": "http://0.0.0.0:8080/",
            "contact_email": "averagejoe@example.com",
            # Activate GUI
            "enable_gui": False,
            "dadjokes_gui": False,
            # Activate API docs
            "enable_docs": False,
            # Base URL for response
            "baseurl": "http://0.0.0.0:8080/"
        }

        self.app = create_app(settings=self.settings)

    def tearDown(self):
        rmtree(self.settings['folder'])

    # Interfaces
    async def test_image_methods(self):
        filename = os.path.join(os.path.dirname(__file__), 'image.gif')

        # Upload image
        async with AsyncClient(
            app=self.app, base_url="http://0.0.0.0:8080/api/3"
        ) as client:
            with open(filename, "rb") as image:
                response = await client.post(
                    '/upload',
                    files={'image': ('image.gif', image)}
                )
        self.assertEqual(response.status_code,  200)
        self.assertEqual(response.json()['success'], True)
        filename = response.json()['data']['deletehash']

        # Get image
        async with AsyncClient(
            app=self.app, base_url="http://0.0.0.0:8080/api/3"
        ) as client:
            response = await client.get(
                f'/image/{filename}'
            )
        self.assertEqual(response.status_code,  200)

        # Delete image
        async with AsyncClient(
            app=self.app, base_url="http://0.0.0.0:8080/api/3"
        ) as client:
            response = await client.delete(
                f'/image/{filename}'
            )
            self.assertEqual(response.status_code,  204)
            response = await client.delete(
                f'/image/{filename}'
            )
            self.assertEqual(response.status_code,  404)

        # Get non existing image
        async with AsyncClient(
            app=self.app, base_url="http://0.0.0.0:8080/api/3"
        ) as client:
            response = await client.get(
                f'/image/{filename}'
            )
        self.assertEqual(response.status_code,  404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
