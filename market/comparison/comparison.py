from typing import Iterator

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.db.models import Value, ImageField
from django.db.models.functions import Concat
from django.http import HttpRequest

from products.models import Product


class Comparison:
    """ Класс сравнения товаров. """

    def __init__(self, request: HttpRequest) -> None:
        """ Инициализация сравнения товаров в сессии. """

        self.session: SessionBase = request.session
        compare = self.session.get(settings.COMPARE_SESSION_ID)
        if not compare:
            compare = self.session[settings.COMPARE_SESSION_ID] = {}
        self.compare = compare

    def __iter__(self) -> Iterator:
        """ Получение данных по товарам и перебор значений. """

        product_ids: list = []
        for val in self.compare.values():
            product_ids.extend(list(val[1].keys()))

        products = Product.objects \
            .select_related("category") \
            .prefetch_related("product_images",
                              "product_properties__property") \
            .filter(id__in=product_ids) \
            .annotate(images=Concat(Value(settings.MEDIA_URL),
                                    "product_images__image",
                                    output_field=ImageField())) \
            .values("id",
                    "name",
                    "category",
                    "images",
                    "property__name",
                    "product_properties__value")

        compare = self.compare.copy()
        for product in products:
            product_id = str(product["id"])
            category_id = str(product["category"])
            name = product["name"]
            product_property_tuple = (product["property__name"],
                                      product["product_properties__value"])
            product_images = product["images"]

            if not compare[category_id][1].get(product_id):
                compare[category_id][1][product_id] = {
                    "name": name,
                    "properties": [],
                    "images": []
                }

            if product_property_tuple not in compare[category_id][1][product_id]["properties"]:
                compare[category_id][1][product_id]["properties"].append(product_property_tuple)

            if product_images not in compare[category_id][1][product_id]["images"]:
                compare[category_id][1][product_id]["images"].append(product_images)

        processed_categories = set()
        for category_id, value in compare.items():

            if value[0] not in processed_categories:
                processed_categories.add(value[0])
                yield {
                    "category_id": category_id,
                    "category_name": value[0],
                }

            for product_id, product_info in value[1].items():
                yield {
                    "category_id": category_id,
                    "category_name": None,
                    "product_id": product_id,
                    "product_name": product_info["name"],
                    "properties": product_info["properties"],
                    "images": product_info["images"]
                }

    def add(self, product: Product) -> None:
        """ Добавление товара в сессию. """

        category_id = str(product.category_id)
        category = product.category.name
        if category_id not in self.compare:
            self.compare[category_id] = [category, {}]

        product_id: str = str(product.id)
        # Проверяем есть ли id товара в сравнении
        if product_id not in self.compare[category_id][1]:
            # добавляем товара
            self.compare[category_id][1][product_id] = {}

        self.save()

    def remove_product(self, category_id, product_id) -> None:
        """ Удаление товара из сессии. """

        if product_id in self.compare[category_id]:
            del self.compare[category_id][product_id]

        self.save()

    def remove_category(self) -> None:
        """ Удаление категории из сессии. """
        pass

    def clear(self):
        """ Удаление списка из сеанса. """

        del self.session[settings.COMPARE_ID]

        self.save()

    def save(self) -> None:
        """ Сохранение изменений в сессии. """

        # self.session[settings.COMPARE_SESSION_ID] = self.compare
        self.session.modified = True
