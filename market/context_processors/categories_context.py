from django.core.cache import cache
from products.models import Category
from settings.models import SiteSettings


def categories(request):
    """ Контекст-процессор для вывода категорий товаров """

    categories_cache_time = 60 * 60 * 24 * SiteSettings.load().categories_cache_time
    all_categories = cache.get('all_categories')
    if not all_categories:
        all_categories = Category.objects.select_related('parent')
        cache.set('all_categories', all_categories, categories_cache_time)
    else:
        actual_categories = Category.objects.select_related('parent')
        if repr(all_categories) != repr(actual_categories):
            cache.delete('all_categories')
            all_categories = actual_categories
            cache.set('all_categories', all_categories, categories_cache_time)
    names = [category.name for category in all_categories]
    icons_paths = []
    for category in all_categories:
        icons_paths.append(f"img/icons/departments/{category.name}.svg")

    return {
        'categories': all_categories.filter(level=0),
        'category_icons_paths': dict(zip(names, icons_paths)),
    }
