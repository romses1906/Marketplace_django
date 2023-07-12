from django.urls import path

from products.views import ProductsByCategoryView, ProductDetailView

app_name = "products"

urlpatterns = [
    path('<int:pk>/', ProductsByCategoryView.as_view(), name='products_by_category'),
    path('item/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
