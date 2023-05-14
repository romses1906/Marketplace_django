from products.models import Category


def categories(request):
    """ Контекст-процессор для вывода категорий на главной странице """

    categories = Category.objects.select_related('parent')
    names = [category.name for category in categories]
    icons_paths = []
    for category in categories:
        icons_paths.append(f"img/icons/departments/{category.name}.svg")

    return {
        'categories': categories.filter(level=0),
        'category_icons_paths': {name: path for name, path in zip(names, icons_paths)},
    }
