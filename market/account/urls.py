from django.urls import path

from .views import AccountUser, ProfileUser, HistorySearchView

app_name = 'account'

urlpatterns = [
    path('<int:pk>/', AccountUser.as_view(), name='account_user'),
    path('<int:pk>/profile/', ProfileUser.as_view(), name='profile_user'),
    path('<int:pk>/history/', HistorySearchView.as_view(), name='history_user'),
]
