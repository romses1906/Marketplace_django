from django.urls import path

from .views import CreateReviewsView

app_name = 'reviews'

urlpatterns = [
    path('create/<int:pk>/', CreateReviewsView.as_view(), name='product_reviews'),
]
