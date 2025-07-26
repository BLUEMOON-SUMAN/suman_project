from django.shortcuts import render 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework.permissions import AllowAny 

import os
from datetime import datetime, timedelta
# from rest_framework import serializers # 이 특정 APIView에서는 Serializer가 직접 사용되지 않으므로 제거 가능

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account
import json

import logging
logger = logging.getLogger(__name__) 

# 환경 변수 로드는 파일 상단에 그대로 유지
GA_SERVICE_ACCOUNT_KEY_JSON = os.environ.get('GOOGLE_ANALYTICS_SERVICE_ACCOUNT_KEY')
GA_PROPERTY_ID = os.environ.get('GA_PROPERTY_ID')

ga_credentials = None
if GA_SERVICE_ACCOUNT_KEY_JSON and GA_PROPERTY_ID:
    try:
        service_account_info = json.loads(GA_SERVICE_ACCOUNT_KEY_JSON)
        ga_credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly'] 
        )
        logger.info("Google Analytics Credentials successfully loaded from environment variable.")
    except json.JSONDecodeError as e:
        logger.error(f"환경 변수에서 Google Analytics 서비스 계정 키 JSON 디코딩 오류: {e}")
    except Exception as e:
        logger.error(f"Google Analytics Credentials 생성 중 일반 오류 발생: {e}")
else:
    logger.warning("GOOGLE_ANALYTICS_SERVICE_ACCOUNT_KEY 또는 GA_PROPERTY_ID 환경 변수가 설정되지 않았습니다. GA 연동 불가.")

# Google Analytics 월별 활성 사용자 데이터를 제공하는 APIView
class AnalyticsMonthlyVisitorsView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        try:
            if not ga_credentials or not GA_PROPERTY_ID:
                logger.error("GA 인증 정보 또는 Property ID가 누락되었습니다.")
                return Response({"error": "GA 인증 정보 누락"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if GA_PROPERTY_ID == 'properties/YOUR_GA4_PROPERTY_ID':
                logger.error("GA Property ID가 기본값으로 설정되어 있습니다. 올바른 ID로 변경해주세요.")
                return Response(
                    {"error": "Google Analytics Property ID is not set or invalid. Cannot fetch data."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            client = BetaAnalyticsDataClient(credentials=ga_credentials)
						
            ######### 최근 6개월 활성 사용자 데이터를 가져오는 로직 (0 방문자 달 포함) ########
            today = datetime.now()
            
            # 응답에 포함되어야 할 최근 6개월의 모든 yearMonth 조합을 미리 생성
            all_target_months = []
            for i in range(6): # 0부터 5까지, 총 6번 반복
                # today에서 i개월 전의 날짜를 계산
                # (today.month - i)가 0 이하면 전년도로 넘어감
                current_month = today.month - i
                current_year = today.year

                while current_month <= 0:
                    current_month += 12
                    current_year -= 1
                
                # YYYYMM 형식으로 저장 (예: 202407)
                all_target_months.append(int(f"{current_year}{current_month:02d}"))
            
            # 가장 오래된 월부터 최신 월 순으로 정렬 (예: [202402, 202403, ..., 202407])
            all_target_months.sort()

            # GA API 요청을 위한 시작 날짜와 종료 날짜 설정
            # all_target_months의 첫 번째 월의 1일이 API 요청의 시작 날짜가 됨
            start_year = all_target_months[0] // 100
            start_month = all_target_months[0] % 100
            start_date_obj = datetime(start_year, start_month, 1)
            start_date = start_date_obj.strftime("%Y-%m-%d")
            
            # API 요청의 종료 날짜는 오늘 날짜
            end_date = today.strftime("%Y-%m-%d")

            logger.info(f"GA Data API 요청 기간 (활성 사용자, 0 포함): {start_date} 부터 {end_date} 까지")

            # GA에 요청 (GA_ID, 날짜범위, 차원(yearMonth), 측정항목(activeUsers))
            monthly_report_request = RunReportRequest(
                property=GA_PROPERTY_ID,
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="yearMonth")],
                metrics=[Metric(name="activeUsers")] 
            )
						
            response = client.run_report(monthly_report_request)
						
            # GA에서 받은 데이터를 yearMonth를 키로 하는 딕셔너리에 저장
            ga_data_map = {}
            for row in response.rows:
                ym = int(row.dimension_values[0].value) 
                active_users = int(row.metric_values[0].value) 
                ga_data_map[ym] = active_users

            # 최종 응답 데이터를 생성
            final_data = []
            for ym in all_target_months:
                # ga_data_map에서 해당 월의 데이터를 찾고, 없으면 0으로 설정
                visitors = ga_data_map.get(ym, 0) 
                final_data.append({"yearMonth": ym, "visitors": visitors})

            logger.info(f"Successfully fetched monthly GA data (activeUsers, with zeros): {final_data}")
            return Response(final_data, status=status.HTTP_200_OK)
				
        except Exception as e:
            logger.error(f"[GA 월별 활성 방문자] 오류: {e}", exc_info=True)
            return Response({"error": "월별 방문자 수 불러오기 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
