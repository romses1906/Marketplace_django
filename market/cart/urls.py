from django.urls import path

from .views import SomeView

app_name = "cart"

urlpatterns = [
    path('some/', SomeView.as_view(), name='some'),
]
