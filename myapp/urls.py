from django.urls import path
from . import views

urlpatterns = [
    path('live/mainlist/', views.BroadcastProductListView.as_view(), name='broadcast-product-list'),
]
