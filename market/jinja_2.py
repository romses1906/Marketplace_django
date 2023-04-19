from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment, FileSystemLoader


class CustomEnvironment(Environment):

    def __init__(self, **options):
        super().__init__()
        self.loader = FileSystemLoader(settings.TEMPLATES[0].get("DIRS"))
        self.globals.update({
            'static': static,
            'url': reverse
        })
