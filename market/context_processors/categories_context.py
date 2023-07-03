from products.models import Category


def categories(request):
    """ Контекст-процессор для вывода категорий на главной странице """

    all_categories = Category.objects.select_related('parent')
    names = [category.name for category in all_categories]
    icons_paths = []
    for category in all_categories:
        icons_paths.append(f"img/icons/departments/{category.name}.svg")

    return {
        'categories': all_categories.filter(level=0),
        'category_icons_paths': dict(zip(names, icons_paths)),
    }
