from django.urls import path

from . import views

app_name = "shops"

urlpatterns = [
    path("<int:pk>/", views.ShopDetailView.as_view(), name="shop-detail"),
    path('t/', views.T.as_view())
]
