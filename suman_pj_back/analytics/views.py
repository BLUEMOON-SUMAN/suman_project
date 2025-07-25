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
						
            ######### 최근 6개월 활성 사용자 데이터를 가져오는 로직 ########
            today = datetime.now()
            # 정확히 6개월 전의 첫째 날을 계산
            target_month = today.month - 5
            target_year = today.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            start_month_date = datetime(target_year, target_month, 1)

            start_date = start_month_date.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")

            logger.info(f"GA Data API 요청 기간 (활성 사용자): {start_date} 부터 {end_date} 까지")

            # GA에 요청 (GA_ID, 날짜범위, 차원(yearMonth), 측정항목(activeUsers))
            monthly_report_request = RunReportRequest(
                property=GA_PROPERTY_ID,
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="yearMonth")],
                metrics=[Metric(name="activeUsers")] # <--- 세션(sessions) 대신 활성 사용자(activeUsers)로 변경
            )
						
            # GA서버 응답값을 response에 저장
            response = client.run_report(monthly_report_request)
						
            data = []
            for row in response.rows:
                ym = int(row.dimension_values[0].value) 
                active_users = int(row.metric_values[0].value) # 측정항목 이름 변경에 따라 변수명도 변경
                data.append({"yearMonth": ym, "visitors": active_users}) # 응답 형식은 visitors로 유지

            # 데이터를 yearMonth 기준으로 오름차순 정렬
            data = sorted(data, key=lambda x: x["yearMonth"])
            
            logger.info(f"Successfully fetched monthly GA data (activeUsers): {data}")
            return Response(data, status=status.HTTP_200_OK)
				
        except Exception as e:
            logger.error(f"[GA 월별 활성 방문자] 오류: {e}", exc_info=True)
            return Response({"error": "월별 방문자 수 불러오기 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
