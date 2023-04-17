from django.urls import path

from products.views import CategoriesListView

app_name = "products"

urlpatterns = [
    path("", CategoriesListView.as_view(), name="categories_list"),
]
