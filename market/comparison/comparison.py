from typing import Iterator

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.db.models import Value, ImageField, Min
from django.db.models.functions import Concat
from django.http import HttpRequest

from products.models import Product


def get_properties(sample: list[str],
                   prop: list[list[str]]) -> list[str]:
    """ Функция создает список свойств продукта

    :param sample: шаблон списка свойств.
    :param prop: список свойств товара.
    :return: общий список свойств.
    """
    title_props = []
    for item in prop:
        title_props.append(item[0])

    new_properties = []
    for elem in sorted(sample):
        if elem not in title_props:
            new_properties.append([elem, "не указано"])
            continue
        for item in prop:
            if elem == item[0]:
                new_properties.append(item)

    return new_properties


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
                              "product_properties__property",
                              "offers") \
            .filter(id__in=product_ids) \
            .annotate(images=Concat(Value(settings.MEDIA_URL),
                                    "product_images__image",
                                    output_field=ImageField()),
                      min_offer_price=Min("offers__price")) \
            .values("id",
                    "name",
                    "category",
                    "images",
                    "property__name",
                    "product_properties__value",
                    "min_offer_price")

        compare = self.compare.copy()
        properties_name = dict()
        for product in products:
            product_id = str(product["id"])
            category_id = str(product["category"])
            name = product["name"]
            if category_id not in properties_name:
                properties_name[category_id] = set()
            properties_name[category_id].add(product["property__name"])
            product_properties = [product["property__name"],
                                  product["product_properties__value"]]
            product_images = product["images"]
            product_price = product["min_offer_price"]

            if not compare[category_id][1].get(product_id):
                compare[category_id][1][product_id] = {
                    "name": name,
                    "properties": [],
                    "images": [],
                    "price": product_price
                }

            if product_properties not in compare[category_id][1][product_id]["properties"]:
                compare[category_id][1][product_id]["properties"].append(product_properties)

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
                    "properties": get_properties(properties_name[category_id],
                                                 product_info["properties"]),
                    # "properties": product_info["properties"], # список свойств
                    "images": product_info["images"],
                    "price": product_info["price"]
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

    def remove_product(self, category_id: str, product_id: str) -> None:
        """ Удаление товара из сессии. """

        if product_id in self.compare[category_id][1]:
            del self.compare[category_id][1][product_id]

        if len(self.compare[category_id][1]) == 0:
            self.remove_category(category_id)

        self.save()

    def remove_category(self, category_id: str) -> None:
        """ Удаление категории из сессии. """

        if category_id in self.compare:
            del self.compare[category_id]

        self.save()

    def clear(self):
        """ Удаление списка из сеанса. """

        del self.session[settings.COMPARE_SESSION_ID]

        self.save()

    def save(self) -> None:
        """ Сохранение изменений в сессии. """

        # self.session[settings.COMPARE_SESSION_ID] = self.compare
        self.session.modified = True
