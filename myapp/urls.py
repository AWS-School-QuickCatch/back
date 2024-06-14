from django.urls import path
from . import views

urlpatterns = [
    path('api/live/mainlist', views.BroadcastProductListView.as_view(), name='broadcast-product-list'),   #홈쇼핑 방송상품 리스트 메인 페이지(홈쇼핑사별 호출)
    path('api/live/details', views.BroadcastProductDetails.as_view(), name='broadcast-product-details'),  #홈쇼핑 방송상품 상세 페이지
    path('api/compare/details', views.SimilarProductList.as_view(), name='similar-product-list')          #유사상품 리스트 호출
]
