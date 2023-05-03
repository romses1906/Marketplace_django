import requests
from django.http import JsonResponse

from django.views import View


class SomeView(View):

    def get(self, *args, **kwargs):

        response = requests.get(url="some_host")
        response.raise_for_status()

        return JsonResponse(
            response.json()
        )