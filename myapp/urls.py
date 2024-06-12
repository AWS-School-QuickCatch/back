from django.urls import path
from . import views

urlpatterns = [
    path('live/mainlist/', views.BroadcastProductListView.as_view(), name='broadcast-product-list'),                    #홈쇼핑 방송상품 리스트(메인) 페이지
    path('live/details/<str:product_id>/', views.BroadcastProductDetails.as_view(), name='broadcast-product-details'),  #홈쇼핑 방송상품 상세 페이지
    path('compare/details/<str:product_id>/', views.SimilarProductList.as_view(), name='similar-product-list')          #유사상품 리스트 호출
]
