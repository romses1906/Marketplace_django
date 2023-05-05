from shops.models import Offer


def properties(request):
    """ Контекст-процессор для вывода названий и значений свойств товаров конкретной категории в фильтре каталога """

    names_properties = {}

    try:
        category_id = request.get_full_path().split('/')[2]
        properties_names_lst = list(
            Offer.objects.select_related('shop', 'product__category').filter(
                product__category=category_id).values_list(
                'product__product_properties__property__name', 'product__product_properties__value'))
        for value in properties_names_lst:
            if value[0] not in names_properties:
                names_properties[value[0]] = {value[1]}
            else:
                names_properties[value[0]].add(value[1])
    except (IndexError, UnboundLocalError):
        pass

    return {
        'names_properties': names_properties,
    }
