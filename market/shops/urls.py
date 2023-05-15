from django.urls import path

from . import views

app_name = "shops"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("shops/<int:pk>/", views.ShopDetailView.as_view(), name="shop-detail"),
]
