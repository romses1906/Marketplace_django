from django.test import TestCase, override_settings
from unittest.mock import patch

from django.urls import reverse


# python manage.py test cart.tests.test_mock

class MockResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = {"Host": "response.mock"}

    def json(self):
        response = {
            "chunk_1": "some content",
            "chunk_2": "bla-bla-bla"
        }

        return response


class TestMockSubdivsRemainsResponse(TestCase):

    @override_settings(DEBUG=True)
    @patch("requests.get", return_value=MockResponse())
    def test_mocked_view(self, mocked):

        mocked.return_value.raise_for_status = lambda: True

        url = reverse("cart:some")
        response = self.client.get(url)

        expected = {
            "chunk_1": "some content",
            "chunk_2": "bla-bla-bla"
        }
        self.assertEqual(expected, response.json())

