from django.urls import path
from . import views

urlpatterns = [
    path('api/live/mainlist', views.BroadcastProductListView.as_view(), name='broadcast-product-list'),   #홈쇼핑 방송상품 리스트 메인 페이지(홈쇼핑사별 호출)
    path('api/live/details', views.BroadcastProductDetails.as_view(), name='broadcast-product-details'),  #홈쇼핑 방송상품 상세 페이지
    path('api/compare/details', views.SimilarProductList.as_view(), name='similar-product-list'),         #유사상품 리스트 호출
    path('api/review', views.ReviewList.as_view(), name='review-list'),                                   #리뷰 데이터 호출
    path('api/live/hotdeallist', views.MainHotdealList.as_view(), name='main-hotdeal-list')               #눈여겨볼 상품 리스트 호출(메인페이지 오른쪽)
]
