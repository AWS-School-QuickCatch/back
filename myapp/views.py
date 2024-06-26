from pymongo import MongoClient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import os

# MongoDB 클라이언트 설정을 위한 함수
def get_mongo_collection(collection_name, db_name='quickcatch'):
    # 환경변수에서 MongoDB 서버의 IP 주소와 포트 번호 읽기
    # mongo_ip       = os.getenv('MONGO_IP')
    # mongo_port     = os.getenv('MONGO_PORT')
    # db_name        = os.getenv('MONGO_DB_NAME')
    # mongo_user     = os.getenv('MONGO_USER')
    # mongo_password = os.getenv('MONGO_PASSWORD')
    
    #로컬 테스트용
    mongo_ip       = "192.168.0.6"
    mongo_port     = 27017
    db_name        = "quickcatch"
    mongo_user     = "quickcatch"
    mongo_password = "pass123"

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
        date       = request.GET.get('date')
        site_names = request.GET.get('site_name')

        if not date or not site_names:
            return Response({"message": "error", "details": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 데이터베이스에 저장된 날짜 형식에 맞춰 변환
            broadcast_date_obj = datetime.strptime(date, '%Y-%m-%d')
            broadcast_date_str = broadcast_date_obj.strftime('%Y%m%d')
        except ValueError:
            return Response({"message": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        # 홈쇼핑사 리스트화
        site_name_list = site_names.split(',')

        # MongoDB 컬렉션 가져오기
        broadcast_collection       = get_mongo_collection('broadcast')
        similar_product_collection = get_mongo_collection('similar_product')
        review_collection          = get_mongo_collection('review')

        # 현재 시간 확인
        now = datetime.now()
        
        #broadcast에서 update_date에 따른 데이터 호출(가장 최근 크롤링 때 update되지 않았다면, 상품 삭제된 것으로 보고 호출하지 X) 처리
        # 1. 방송이 오늘이거나, 지났거나
        if broadcast_date_obj.date() <= now.date():
            update_date_obj = broadcast_date_obj - timedelta(days=1)
            query = {
                "site_name"     : {"$in": site_name_list},
                "broadcast_date": broadcast_date_str,
                "$or": [
                    {"update_date": update_date_obj.strftime('%Y%m%d')},   # update_date = broadcast_date - 1 인 상품만 최신 상품으로 간주
                    {"update_date": broadcast_date_obj.strftime('%Y%m%d')} # update_date = broadcast_date 일 경우
                ]
            }
        # 2. 방송이 오늘 이후 미래인 경우
        else:
            update_date_obj = now - timedelta(days=1)
            query = {
                "site_name"     : {"$in": site_name_list},
                "broadcast_date": broadcast_date_str,
                "$or": [
                    {"update_date": update_date_obj.strftime('%Y%m%d')},  # update_date = 오늘 날짜 - 1 인 상품만 최신 상품으로 간주
                    {"update_date": now.strftime('%Y%m%d')}               # update_date = 오늘 일 경우
                ]
            }
        schedules = list(broadcast_collection.find(query))

        product_list = []
        for schedule in schedules:
            # 값 초기화
            broadcast_start_datetime = None
            broadcast_end_datetime   = None

            # 'N/A' 예외 처리 위한 조건 추가
            if schedule['start_time'] != 'N/A' and schedule['end_time'] != 'N/A':
                try:
                    broadcast_start_datetime = datetime.combine(now.date(), datetime.strptime(schedule['start_time'], '%H:%M').time())
                    broadcast_end_datetime   = datetime.combine(now.date(), datetime.strptime(schedule['end_time'], '%H:%M').time())

                    start_datetime_add_9 = broadcast_start_datetime + timedelta(hours=-9)
                    end_datetime_add_9   = broadcast_end_datetime + timedelta(hours=-9)

                    # 현재 시간 기준으로 라이브 방송 여부 판단
                    now_live_yn = 'Y' if start_datetime_add_9 <= now <= end_datetime_add_9 else 'N'

                    # Fetch similar products from MongoDB
                    similar_products = list(similar_product_collection.find({
                        "product_id": schedule['product_id']
                    }))

                    similar_product_list = []
                    for similar_product in similar_products:
                        similar_product_list.extend(similar_product['similar_products'])

                    # Sort the similar products by price and select top 3
                    similar_product_list = sorted(similar_product_list, key=lambda x: int(x['price']))[:3]

                    #review 요약 여부 확인, 각 홈쇼핑사 별 기준 다름(cjonstyle:100개/gsshop&hmall:30개/lottemall:?)
                    review_details = review_collection.find_one({"product_id":  schedule['product_id']})
                    if review_details and schedule['site_name']=="cjonstyle" and review_details['total_reviews'] >= 100:
                        review_yn = "Y"
                    elif review_details and (schedule['site_name']=="hmall" or schedule['site_name']=="gsshop") and review_details['total_reviews'] >= 30: 
                        review_yn = "Y"
                    else:
                        review_yn = "N"

                    product_data = {
                        "p_id"       : schedule['product_id'],
                        "p_name"     : schedule['name'],
                        "p_price"    : schedule['price'],
                        "site_name"  : schedule['site_name'],
                        "now_live_yn": now_live_yn,
                        "img_url"    : schedule['image_url'],
                        "start_time" : schedule['start_time'],
                        "end_time"   : schedule['end_time'],
                        "review_yn"  : review_yn,
                        "similar_product_list": similar_product_list
                    }
                    product_list.append(product_data)
                except ValueError:
                    continue  # 날짜 변환 실패 시 다음 schedule로 넘어감

        # product_list를 start_time을 기준으로 오름차순 정렬
        product_list = sorted(product_list, key=lambda x: x['start_time'])

        response_data = {
            "message": "success",
            "result" : {
                "broadcast_date": broadcast_date_str,
                "product_list"  : product_list
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

# 해당 product_id에 대한 유사상품 호출
class ReviewList(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')

        if not product_id:
            return Response({"message": "error", "details": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)            

        try:
            # MongoDB 컬렉션 가져오기
            review_collection = get_mongo_collection('review')
            
            # 해당 product_id에 대한 리뷰 조회
            review_details = review_collection.find_one({"product_id": product_id})

            if not review_details:
                return Response({"message": "error", "details": "Product information not found"}, status=status.HTTP_404_NOT_FOUND)

            review_data = {
                "product_id"             : review_details.get('product_id'),
                "average_negative"       : review_details.get('average_negative'),
                "average_neutral"        : review_details.get('average_neutral'),
                "average_positive"       : review_details.get('average_positive'),
                "negative_review_summary": review_details.get('negative_review_summary'),
                "positive_review_summary": review_details.get('positive_review_summary'),
                "total_reviews"          : review_details.get('total_reviews')
            }

            response_data = {
                "message": "success",
                "result": {
                    "review_details": review_data
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)