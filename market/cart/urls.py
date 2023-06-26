from django.urls import path
from cart.views import CartView, UpdateCartView, RemoveFromCartView

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('update/', UpdateCartView.as_view(), name='update_to_cart'),
    path('remove/<int:product_id>', RemoveFromCartView.as_view(), name='remove_from_cart'),
]
