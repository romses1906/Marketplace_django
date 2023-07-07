import os

from django.test import TestCase, Client
from django.test import signals
from django.urls import reverse
from jinja2 import Template as Jinja2Template

from config.settings import FIXTURE_DIRS
from settings.models import SiteSettings
from shops.models import Shop, Banner, Offer
from shops.utils import get_time_left

ORIGINAL_JINJA2_RENDERER = Jinja2Template.render


def instrumented_render(template_object, *args, **kwargs):
    """ Переопределение метода рендеринга шаблонов Jinja2 """

    context = dict(*args, **kwargs)
    signals.template_rendered.send(
        sender=template_object,
        template=template_object,
        context=context
    )
    return ORIGINAL_JINJA2_RENDERER(template_object, *args, **kwargs)


Jinja2Template.render = instrumented_render


class ShopDetailViewTest(TestCase):
    """ Тестирование детального представления магазина """
    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json"
    ]

    def setUp(self):
        self.client = Client()
        self.shop = Shop.objects.get(id=1)
        kwargs = {
            "pk": self.shop.pk,
        }
        url = reverse("shops:shop-detail", kwargs=kwargs)
        self.response = self.client.get(url)

    def test_view_returns_correct_HTTP_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        self.assertTemplateUsed(self.response, "shops/shop_detail.j2")


class TestHomePageView(TestCase):
    """ Тестирование главной страницы магазина """
    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()
        self.num_hot_deals = SiteSettings.load().hot_deals
        self.num_top_product_count = SiteSettings.load().top_product_count
        self.num_limited_edition = SiteSettings.load().limited_edition_count
        self.url = reverse('shops:home')
        self.response = self.client.get(self.url)

    def test_homepage_view(self):
        """ Тест главной страницы магазина """
        self.assertEqual(self.response.status_code, 200)
        days, hours, minutes, seconds = get_time_left()
        self.assertEqual(self.response.context_data['days'], days)
        self.assertEqual(self.response.context_data['hours'], hours)
        self.assertEqual(self.response.context_data['minutes'], minutes)
        self.assertTrue(all(isinstance(banner, Banner) for banner in self.response.context_data['banners']))
        self.assertTrue(len(self.response.context_data['top_products']) <= self.num_top_product_count)
        self.assertTrue(len(self.response.context_data['top_products']) > 0)
        self.assertTrue(len(self.response.context_data['hot_deals']) <= self.num_hot_deals)
        self.assertTrue(len(self.response.context_data['hot_deals']) > 0)
        self.assertTrue(self.response.context_data['limited_edition_products'].exists())
        self.assertTrue(self.response.context_data['hot_deals'].exists())
        self.assertTrue(self.response.context_data['top_products'].exists())
        self.assertTrue(len(self.response.context_data['limited_edition_products']) > 0)

        offer_of_the_day = self.response.context_data['offer_of_the_day']
        if offer_of_the_day:
            self.assertIsInstance(offer_of_the_day, Offer)
            self.assertTrue(offer_of_the_day.limited_edition)
            self.assertContains(self.response, offer_of_the_day.product.name)

    def test_view_renders_desired_template(self):
        """ Тестирование испоьзования ожидаемого шаблона для рендеринга страницы """

        self.assertTemplateUsed(self.response, "home.j2")
