from django.urls import path
from order.views import Step1View, Step2View, Step3View, Step4View, OrderDetailView, OrderListView, Step1NAView

app_name = 'order'

urlpatterns = [
    path('step1/', Step1View.as_view(), name='step1'),
    path('step1na/', Step1NAView.as_view(), name='step1na'),
    path('step2/', Step2View.as_view(), name='step2'),
    path('step3/', Step3View.as_view(), name='step3'),
    path('step4/', Step4View.as_view(), name='step4'),
    path('<int:pk>/', OrderDetailView.as_view(), name='detail_order'),
    path('', OrderListView.as_view(), name='history'),
]
