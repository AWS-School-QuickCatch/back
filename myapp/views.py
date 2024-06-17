from pymongo import MongoClient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime
import os

# MongoDB 클라이언트 설정을 위한 함수
def get_mongo_collection(collection_name, db_name='quickcatch'):
    # 환경변수에서 MongoDB 서버의 IP 주소와 포트 번호 읽기
    mongo_ip       = os.getenv('MONGO_IP', '43.203.249.162')
    mongo_port     = os.getenv('MONGO_PORT', '27017')
    db_name        = os.getenv('MONGO_DB_NAME', db_name)
    mongo_user     = os.getenv('MONGO_USER', 'quickcatch')
    mongo_password = os.getenv('MONGO_PASSWORD', 'pass123')

    # 포트 번호는 정수로 변환
    mongo_port = int(mongo_port)

    # MongoDB URI 생성
    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_ip}:{mongo_port}/{db_name}"
    
    # MongoDB 클라이언트 설정
    # client     = MongoClient(mongo_ip, mongo_port, mongo_password)
    client     = MongoClient(mongo_uri)
    db         = client[db_name]
    collection = db[collection_name]
    return collection

# 홈쇼핑 방송상품 리스트(메인) 호출(해당 홈쇼핑사별)
class BroadcastProductListView(APIView):
    def get(self, request, *args, **kwargs):
        date      = request.GET.get('date')
        site_name = request.GET.get('site_name')
        
        if not date or not site_name:
            return Response({"message": "error", "details":  "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 데이터베이스에 저장된 날짜 형식에 맞춰 변환
            broadcast_date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
        except ValueError:
            return Response({"message": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        
        # MongoDB 컬렉션 가져오기
        broadcast_collection = get_mongo_collection('broadcast')
        
        # 방송 스케줄 필터링
        schedules = list(broadcast_collection.find({
            "broadcast_date": broadcast_date,
            "site_name"     : site_name
        }))

        #현재 시간 확인
        now = datetime.datetime.now()
        
        product_list = []
        for schedule in schedules:
            # 값 초기화
            broadcast_start_datetime = ''
            broadcast_end_datetime = ''

            # 'N/A' 예외 처리 위한 조건 추가
            if schedule['start_time'] != 'N/A' and schedule['end_time'] != 'N/A':
                #now_live_yn = "Y" if schedule['start_time'] <= datetime.datetime.now().strftime('%H:%M:%S') <= schedule['end_time'] else "N"
                broadcast_start_datetime = datetime.datetime.combine(now.date(), datetime.datetime.strptime(schedule['start_time'], '%H:%M').time())
                broadcast_end_datetime   = datetime.datetime.combine(now.date(), datetime.datetime.strptime(schedule['end_time'], '%H:%M').time())
                
                start_datetime_add_9 =  broadcast_start_datetime + datetime.timedelta(hours=-9)
                end_datetime_add_9   = broadcast_end_datetime + datetime.timedelta(hours=-9)

                # 현재 시간 기준으로 라이브 방송 여부 판단
                now_live_yn  = 'Y' if start_datetime_add_9 <= now <= end_datetime_add_9 else 'N'
                product_data = {
                    "p_id"           : schedule['product_id'],
                    "p_name"         : schedule['name'],
                    "p_price"        : schedule['price'],
                    "now_live_yn"    : now_live_yn,
                    "img_url"        : schedule['image_url'],
                    "start_time"     : schedule['start_time'],
                    "end_time"       : schedule['end_time'],
                }
                product_list.append(product_data)

        response_data = {
            "message": "success",
            "result" : {
                "broadcast_date" : broadcast_date,
                "site_name"      : site_name,
                "product_list"   : product_list
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

# 홈쇼핑 방송상품 상세 페이지
class BroadcastProductDetails(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')

        if not product_id:
            return Response({"message": "error", "details":  "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)    
       
        try:
            # MongoDB 컬렉션 가져오기
            broadcast_collection = get_mongo_collection('broadcast')
            
            # 해당 product_id에 대한 상품 정보 조회
            search_product = broadcast_collection.find_one({"product_id": product_id})
            
            if not search_product:
                raise Exception("Product information not found")
            
            # broadcast_schedule.broadcast_time_start와 broadcast_schedule.broadcast_time_end를 datetime 형식으로 변환
            now = datetime.datetime.now()
            broadcast_start_datetime = datetime.datetime.combine(now.date(), datetime.datetime.strptime(search_product['start_time'], '%H:%M').time())
            broadcast_end_datetime   = datetime.datetime.combine(now.date(), datetime.datetime.strptime(search_product['end_time'], '%H:%M').time())

            start_datetime_add_9 =  broadcast_start_datetime + datetime.timedelta(hours=-9)
            end_datetime_add_9   = broadcast_end_datetime + datetime.timedelta(hours=-9)
            
            # 현재 시간 기준으로 라이브 방송 여부 판단
            now_live_yn = 'Y' if start_datetime_add_9 <= now <= end_datetime_add_9 else 'N'
            
            response_data = {
                "message": "success",
                "details": {
                    "site_name"       : search_product['site_name'],
                    "p_id"            : search_product['product_id'],
                    "p_name"          : search_product['name'],
                    "broadcast_date"  : search_product['broadcast_date'],
                    "p_price"         : search_product['price'],
                    "now_live_yn"     : now_live_yn,
                    "img_url"         : search_product['image_url'],
                    "start_time"      : search_product['start_time'],
                    "end_time"        : search_product['end_time'],
                    "redirect_url"    : search_product['redirect_url'],
                    "img_url_details" : search_product['detail_images']
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "error", "details": str(e)}, status=status.HTTP_404_NOT_FOUND)

# 해당 product_id에 대한 유사상품 호출
class SimilarProductList(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')

        if not product_id:
            return Response({"message": "error", "details":  "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)            
        
        try:
            # MongoDB 컬렉션 가져오기
            similar_product_collection = get_mongo_collection('similar_product')
            
            # 해당 product_id에 대한 유사상품 전체 조회
            similar_products = list(similar_product_collection.find({"product_id": product_id}))

            if len(similar_products) == 0:
                 return Response({"message": "error", "details":  "Product information not found"}, status=status.HTTP_404_NOT_FOUND)
                     
            product_list = []
            for similar_product in similar_products:

                s_product_data= {
                    "p_id"           : similar_product['product_id'],
                    "s_name"         : similar_product['product_name'],
                    "s_price"        : similar_product['price'],
                    "seller"         : similar_product['seller'],
                    "img_url"        : similar_product['image_url'],
                    "redirect_url"   : similar_product['redirect_url'],   
                }

                product_list.append(s_product_data)

            response_data = {
                "message": "success",
                "result" : {
                    "product_list": product_list
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
