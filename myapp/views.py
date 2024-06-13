from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Product, HomeShopping, BroadcastSchedule, BroadcastProduct, SimilarProduct
# import datetime
from datetime import datetime 

#홈쇼핑 방송상품 리스트(메인) 페이지
class BroadcastProductListView(APIView):

    def get(self, request, *args, **kwargs):
        date = request.GET.get('date')
        site_name_1 = request.GET.get('site_name_1')
        site_name_2 = request.GET.get('site_name_2')
        site_name_3 = request.GET.get('site_name_3')

        if not date or not site_name_1 or not site_name_2 or not site_name_3:
            return Response({"message": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            broadcast_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"message": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        sites = [site_name_1, site_name_2, site_name_3]
        home_shopping_sites = HomeShopping.objects.filter(home_shopping_id__in=sites)

        result_list = []

        for site in home_shopping_sites:
            # BroadcastSchedule에서 날짜와 홈쇼핑사로 필터링
            schedules = BroadcastSchedule.objects.filter(
                broadcast_date=broadcast_date,
                product__home_shopping=site
            )
            product_list = []

            for schedule in schedules:
                product = schedule.product
                now_live_yn = "Y" if schedule.broadcast_time_start <= datetime.now().time() <= schedule.broadcast_time_end else "N"
                product_data = {
                    "p_id": product.product_id,
                    "p_name": product.product_name,
                    "p_price": f"{product.price:,}원",
                    "live_time": schedule.broadcast_time_start.strftime("%H:%M:%S") if schedule else None,
                    "now_live_yn": now_live_yn,
                    "img_url": product.product_image_url,
                    "p_url": product.product_url,
                    "live_start_time": schedule.broadcast_time_start.strftime("%H:%M:%S") if schedule else None,
                    "live_end_time": schedule.broadcast_time_end.strftime("%H:%M:%S") if schedule else None
                }
                product_list.append(product_data)

            result_list.append({
                "site_name": site.name,
                "products": product_list
            })

        response_data = {
            "message": "success",
            "date": date,
            "list": result_list
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
#홈쇼핑 방송상품 상세 페이지
class BroadcastProductDetails(APIView):
    def get(self, request, product_id):
        try:
            # 해당 product_id에 대한 상품 정보 조회
            product            = Product.objects.get(product_id=product_id)
            broadcast_schedule = BroadcastSchedule.objects.get(product_id=product_id)
            broadcast_product  = BroadcastProduct.objects.get(product_id=product_id)
            
            # broadcast_schedule.broadcast_time_start와 broadcast_schedule.broadcast_time_end를 datetime 형식으로 변환
            now = datetime.now()
            broadcast_start_datetime = datetime.combine(now.date(), broadcast_schedule.broadcast_time_start)
            broadcast_end_datetime   = datetime.combine(now.date(), broadcast_schedule.broadcast_time_end)

            # 현재 시간 기준으로 라이브 방송 여부 판단
            now_live_yn = 'y' if broadcast_start_datetime <= now <= broadcast_end_datetime else 'n'
            
            response_data = {
                "message": "success",
                "details": {
                    "site_name"      : product.home_shopping.name,
                    "p_id"           : product.product_id,
                    "p_name"         : product.product_name,
                    "p_price"        : product.price,
                    "live_time"      : broadcast_schedule.broadcast_time_start,
                    "now_live_yn"    : now_live_yn,
                    "img_url"        : product.product_image_url,
                    "live_url"       : broadcast_product.product_video_url,
                    "sales_url"      : product.product_url,
                    "live_start_time": broadcast_schedule.broadcast_time_start,
                    "live_end_time"  : broadcast_schedule.broadcast_time_end
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except (Product.DoesNotExist, BroadcastSchedule.DoesNotExist, BroadcastProduct.DoesNotExist):
            return Response({"message": "error", "details": "Product information not found."}, status=status.HTTP_404_NOT_FOUND)
        
#유사상품 리스트 호출
class SimilarProductList(APIView):
    def get(self, request, product_id):
        # 해당 product_id에 대한 SimilarProduct 조회
        similar_products = SimilarProduct.objects.filter(product_id=product_id)

        # similar_products가 비어 있는지 확인
        if not similar_products:
            return Response({"message": "error", "details": "Similar product information not found."}, status=status.HTTP_404_NOT_FOUND)

        compare_list = []

        for similarProduct in similar_products:
            product_info = {
                "p_id"      : similarProduct.product_id,
                "site_name" : similarProduct.seller,
                "p_name"    : similarProduct.product_name,
                "p_price"   : similarProduct.price,
                "img_url"   : similarProduct.product_image_url,
                "sales_url" : similarProduct.product_url
            }
            compare_list.append(product_info)

        response_data = {
            "message": "success",
            "compare_list": compare_list
        }

        return Response(response_data, status=status.HTTP_200_OK)