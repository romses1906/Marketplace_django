import django_filters
from django import forms

from shops.models import Offer


class ProductFilter(django_filters.FilterSet):
    """ Класс для фильтрации товаров в конкретной категории по различным параметрам """

    price = django_filters.RangeFilter()
    product_name = django_filters.CharFilter(label="Название продукта", field_name="product__name",
                                             lookup_expr='icontains',
                                             widget=forms.TextInput(attrs={'placeholder': "Название"}))
    multiple_shops = django_filters.MultipleChoiceFilter(choices=[], label="Магазины", method="multiple_shops_method",
                                                         widget=forms.CheckboxSelectMultiple(
                                                             attrs={"class": "form-control"}))

    class Meta:
        model = Offer
        fields = ['price', 'product_name', 'multiple_shops']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = kwargs['queryset'][0].product.category
        self.form.fields['multiple_shops'].choices = self.get_multiple_shops_choices()

    def get_multiple_shops_choices(self):
        """ Метод для получения параметров выбора для фильтрации товаров по продавцам """

        shops_choices = list(
            Offer.objects.select_related('shop', 'product').filter(product__category=self.category).values_list(
                'shop__id', 'shop__name').distinct('shop__id'))
        return shops_choices

    def multiple_shops_method(self, queryset, name, value):
        """ Метод фильтрации товаров по выбранным пользователем продавцам """

        ids = []
        for item in value:
            if item != "":
                ids.append(item)
        if len(ids):
            qs = queryset.filter(shop__in=ids)
        else:
            qs = queryset
        return qs
