from django.urls import path

from .views import CompareDetail, add_compare_view

app_name = "comparison"

urlpatterns = [
    path("", CompareDetail.as_view(), name="compare-detail"),
    path("add/<int:product_id>", add_compare_view, name="add-to-compare"),
]
