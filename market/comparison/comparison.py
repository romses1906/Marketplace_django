from typing import Iterator

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.db.models import Value, ImageField, Min
from django.db.models.functions import Concat
from django.http import HttpRequest

from products.models import Product


def get_properties(sample: list[str], props: list[list[str]]) -> list[str]:
    """ Функция создает список свойств товаров, по общему списку свойств всех товаров

    :param sample: шаблон списка свойств.
    :param props: список свойств товара.
    :return: общий список свойств.
    """
    title_props = []
    for prop in props:
        prop_name = prop[0]
        title_props.append(prop_name)

    new_properties = []
    for elem in sorted(sample):
        if elem not in title_props:
            new_properties.append([elem, "не указано"])
            continue
        for prop in props:
            prop_name = prop[0]
            if elem == prop_name:
                new_properties.append(prop)

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

        # получаем все id товаров во всех категориях
        all_product_ids: list = []
        for val in self.compare.values():
            product_ids = list(val[1].keys())
            all_product_ids.extend(product_ids)

        queryset = Product.objects \
            .select_related("category") \
            .prefetch_related("product_images",
                              "product_properties__property",
                              "offers") \
            .filter(id__in=all_product_ids) \
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
        unique_property_names = dict()

        # формируем словарь для выдачи
        for product in queryset:
            product_id = str(product["id"])
            category_id = str(product["category"])
            product_name = product["name"]
            if category_id not in unique_property_names:
                unique_property_names[category_id] = set()
            unique_property_names[category_id].add(product["property__name"])
            product_property = [product["property__name"],
                                product["product_properties__value"]]
            product_image = product["images"]
            product_price = str(product["min_offer_price"])

            products = compare[category_id][1]
            if not products.get(product_id):
                products[product_id] = {
                    "product_name": product_name,
                    "properties": [],
                    "images": [],
                    "price": product_price
                }

            product_properties = compare[category_id][1][product_id]["properties"]
            if product_property not in product_properties:
                product_properties.append(product_property)

            product_images = compare[category_id][1][product_id]["images"]
            if product_image not in product_images:
                product_images.append(product_image)

        processed_categories = set()

        for category_id, value in compare.items():

            category_name = value[0]
            if category_name not in processed_categories:
                processed_categories.add(category_name)
                yield {
                    "category_id": category_id,
                    "category_name": category_name,
                }

            products = value[1]
            for product_id, product_info in products.items():
                yield {
                    "category_id": category_id,
                    "category_name": None,
                    "product_id": product_id,
                    "product_name": product_info["product_name"],
                    "properties": get_properties(unique_property_names[category_id],
                                                 product_info["properties"]),
                    "images": product_info["images"],
                    "price": product_info["price"]
                }

    def add(self, product: Product) -> None:
        """ Добавление товара в сессию. """

        category_id = str(product.category_id)
        category_name = product.category.name
        if category_id not in self.compare:
            self.compare[category_id] = [category_name, {}]

        product_id: str = str(product.id)
        products = self.compare[category_id][1]
        # Проверяем есть ли id товара в сравнении
        if product_id not in products:
            # добавляем товара
            products[product_id] = {}

        self.save()

    def remove_product(self, category_id: str, product_id: str) -> None:
        """ Удаление товара из сессии. """

        products = self.compare[category_id][1]
        if product_id in products:
            del products[product_id]

        if len(products) == 0:
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
