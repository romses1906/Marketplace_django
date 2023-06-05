from django.urls import path
from .views import clear_all_cache_view, DiscountsListView

app_name = 'settings'

urlpatterns = [
    path('clear_all_cache/', clear_all_cache_view, name='clear_all_cache'),
    path("sales/", DiscountsListView.as_view(), name="sales"),

]
