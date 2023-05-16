from django.urls import path
from .views import FileUploadView

app_name = 'imports'

urlpatterns = [
    path('upload/<int:pk>/', FileUploadView.as_view(), name='upload_file')
]
