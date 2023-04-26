from django.urls import path

from products.views import CategoriesListView, ProductsByCategoryView, ProductDetailView

app_name = "products"

urlpatterns = [
    path("", CategoriesListView.as_view(), name="categories_list"),
    path('<int:pk>/', ProductsByCategoryView.as_view(), name='products_by_category'),
    path('item/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
