import re

import django_filters
from django import forms
from django.core.cache import cache
from django.db.models import Count, Sum
from products.models import ProductProperty, Category
from settings.models import SiteSettings
from shops.models import Offer


class ProductFilter(django_filters.FilterSet):
    """ Класс для фильтрации и сортировки товаров в конкретной категории по различным параметрам """

    SORT_BY_CHOICES = (
        ('price', 'По возрастанию цены'),
        ('-price', 'По убыванию цены'),
        ('reviews', 'По возрастанию кол-ва отзывов'),
        ('-reviews', 'По убыванию кол-ва отзывов'),
        ('created', 'Сначала старые'),
        ('-created', 'Сначала новые'),
        ('popularity', 'По возрастанию кол-ва покупок'),
        ('-popularity', 'По убыванию кол-ва покупок'),

    )

    price = django_filters.RangeFilter()
    product_name = django_filters.CharFilter(label="Название продукта", field_name="product__name",
                                             lookup_expr='icontains',
                                             widget=forms.TextInput(attrs={'placeholder': "Название"}))
    multiple_shops = django_filters.MultipleChoiceFilter(choices=[], label="Магазины", method="multiple_shops_method",
                                                         widget=forms.CheckboxSelectMultiple(
                                                             attrs={"class": "form-control"}))

    multiple_properties = django_filters.MultipleChoiceFilter(choices=[], label="Характеристики",
                                                              method="multiple_properties_method",
                                                              widget=forms.CheckboxSelectMultiple(
                                                                  attrs={"class": "form-control"}))

    sort_by = django_filters.MultipleChoiceFilter(choices=SORT_BY_CHOICES, label="Сортировка",
                                                  method="update_cache_by_sorting",
                                                  widget=forms.CheckboxSelectMultiple(
                                                      attrs={"class": "form-control"}))

    class Meta:
        model = Offer
        fields = ['price', 'product_name', 'multiple_shops', 'multiple_properties', 'sort_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category_id = re.search(r'(?<=catalog/)\d+(?=/)', self.request.get_full_path())[0]
        self.category = Category.objects.get(id=category_id)
        self.form.fields['multiple_shops'].choices = self.get_multiple_shops_choices()
        self.form.fields['multiple_properties'].choices = self.get_multiple_properties_choices()
        self.kwargs = kwargs

    def get_multiple_shops_choices(self):
        """ Метод для получения параметров выбора для фильтрации товаров по продавцам """

        shops_choices = list(
            Offer.objects.select_related('shop', 'product').filter(product__category=self.category).values_list(
                'shop__id', 'shop__name').distinct('shop__id').order_by('shop__id'))

        return shops_choices

    def get_multiple_properties_choices(self):
        """ Метод для получения параметров выбора для фильтрации товаров по характеристикам """

        properties_choices = list(
            Offer.objects.select_related('shop', 'product').filter(product__category=self.category).values_list(
                'product__product_properties__value', 'product__product_properties__value').distinct(
                'product__product_properties__value').order_by('product__product_properties__value'))

        return properties_choices

    def multiple_shops_method(self, queryset, name, value):
        """ Метод фильтрации товаров по выбранным пользователем продавцам """

        ids = []
        for item in value:
            if item != "":
                ids.append(item)
        if ids:
            qs = queryset.filter(shop__in=ids)
        else:
            qs = queryset
        return qs

    def multiple_properties_method(self, queryset, name, value):
        """ Метод фильтрации товаров по выбранным пользователем значениям характеристик """

        names_properties = {}
        values = []
        for item in value:
            if item != "":
                values.append(item)
        if values:
            for val in values:
                name_property = list(ProductProperty.objects.select_related('property').filter(
                    value=val).values_list('property__name'))[0][0]
                if name_property not in names_properties:
                    names_properties[name_property] = {val}
                else:
                    names_properties[name_property].add(val)
            qs = queryset
            for value_prop in names_properties.values():
                qs = qs.select_related('shop', 'product__category').filter(
                    product__product_properties__value__in=value_prop).order_by('product__id').distinct(
                    'product__id')
        else:
            qs = queryset
        return qs

    def multiple_sorting_method(self, queryset, value):
        """ Метод сортировки товаров по выбранным пользователем характеристикам """

        sorting_products = None
        if value[0] == self.SORT_BY_CHOICES[0][0]:
            sorting_products = queryset.order_by("price").distinct("price")
        elif value[0] == self.SORT_BY_CHOICES[1][0]:
            sorting_products = queryset.order_by("-price").distinct("price")
        elif value[0] == self.SORT_BY_CHOICES[4][0]:
            sorting_products = queryset.order_by("created").distinct("created")
        elif value[0] == self.SORT_BY_CHOICES[5][0]:
            sorting_products = queryset.order_by("-created").distinct("created")
        elif value[0] == self.SORT_BY_CHOICES[2][0]:
            sorting_products = queryset.annotate(cnt=Count('product__product_reviews')).order_by('cnt').distinct()
        elif value[0] == self.SORT_BY_CHOICES[3][0]:
            sorting_products = queryset.annotate(cnt=Count('product__product_reviews')).order_by('-cnt').distinct()
        elif value[0] == self.SORT_BY_CHOICES[6][0]:
            sorting_products = queryset.filter(order__status='paid').annotate(
                total_quantity=Sum('orderitem__quantity')).order_by('total_quantity').distinct()
        elif value[0] == self.SORT_BY_CHOICES[7][0]:
            sorting_products = queryset.filter(order__status='paid').annotate(
                total_quantity=Sum('orderitem__quantity')).order_by('-total_quantity').distinct()
        return sorting_products

    def update_cache_by_sorting(self, queryset, name, value):
        """ Метод для учета сортировки при формировании кеша каталога товаров """

        products_cache_time = 60 * 60 * 24 * SiteSettings.load().product_cache_time
        sorting_products = cache.get('sorting_products')
        if not sorting_products:
            sorting_products = self.multiple_sorting_method(queryset, value)
            cache.set('sorting_products', sorting_products, products_cache_time)
        else:
            actual_sorting_products = self.multiple_sorting_method(queryset, value)
            if repr(sorting_products) != repr(actual_sorting_products):
                cache.delete('sorting_products')
                sorting_products = actual_sorting_products
                cache.set('sorting_products', sorting_products, products_cache_time)
        return sorting_products
