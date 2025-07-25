from django.shortcuts import render
# suman_project/suman_pj_back/analytics/views.py

from rest_framework import viewsets, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
import os
from datetime import datetime, timedelta
from rest_framework import serializers

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account
import json

import logging
logger = logging.getLogger(__name__) # 이제 이 로거는 analytics 앱의 로그를 남길 것입니다.

GA_SERVICE_ACCOUNT_KEY_JSON = os.environ.get('GOOGLE_ANALYTICS_SERVICE_ACCOUNT_KEY')
GA_PROPERTY_ID = os.environ.get('GA_PROPERTY_ID', 'properties/497127177')

ga_credentials = None
if GA_SERVICE_ACCOUNT_KEY_JSON and GA_PROPERTY_ID: # 두 변수 모두 존재하는지 확인
    try:
        # 환경 변수에서 읽어온 JSON 문자열을 파이썬 딕셔너리로 변환
        service_account_info = json.loads(GA_SERVICE_ACCOUNT_KEY_JSON)
        # 딕셔너리에서 Google Credentials 객체 생성 (from_service_account_file 대신 from_service_account_info 사용)
        ga_credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly'] # 스코프도 여기서 지정
        )
        logger.info("Google Analytics Credentials successfully loaded from environment variable.")
    except json.JSONDecodeError as e:
        logger.error(f"환경 변수에서 Google Analytics 서비스 계정 키 JSON 디코딩 오류: {e}")
        # 이 오류가 발생하면 Render 로그에서 환경 변수 Value의 JSON 포맷을 다시 확인해야 합니다.
    except Exception as e:
        logger.error(f"Google Analytics Credentials 생성 중 일반 오류 발생: {e}")
else:
    logger.warning("GOOGLE_ANALYTICS_SERVICE_ACCOUNT_KEY 또는 GA_PROPERTY_ID 환경 변수가 설정되지 않았습니다. GA 연동 불가.")
    


class AnalyticsDataSerializer(serializers.Serializer):
    total_users = serializers.IntegerField(read_only=True)
    change_percentage = serializers.FloatField(read_only=True)

# Google Analytics Data API를 통해 방문자 통계 데이터를 제공하는 ViewSet
class AnalyticsDataViewSet(GenericViewSet):
    serializer_class = AnalyticsDataSerializer
    queryset = [] # 모델과 연결되지 않으므로 더미로 둡니다.

    def list(self, request, *args, **kwargs):
        try:
            # credentials가 로드되지 않았다면 에러 반환
            if not ga_credentials:
                return Response(
                    {"error": "Google Analytics Credentials not loaded. Cannot fetch data. Check server logs."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # GA_PROPERTY_ID가 없거나 기본값이라면 에러 반환
            if not GA_PROPERTY_ID or GA_PROPERTY_ID == 'properties/YOUR_GA4_PROPERTY_ID':
                 return Response(
                    {"error": "Google Analytics Property ID is not set or invalid. Cannot fetch data."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # --- 1. 현재까지의 총 방문 횟수 (세션 수) 조회 ---
            total_visits_request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date="2020-01-01", end_date="today")],
                metrics=[Metric(name="sessions")],
            )
            total_visits_response = client.run_report(total_visits_request)
            total_users_count = 0
            if total_visits_response.rows:
                total_users_count = int(total_visits_response.rows[0].metric_values[0].value)

            # --- 2. 지난 한 달 대비 방문 횟수 (세션 수) 변화율 계산 ---
            today = datetime.now()
            current_period_start = (today - timedelta(days=29)).strftime('%Y-%m-%d')
            current_period_end = today.strftime('%Y-%m-%d')
            previous_period_start = (today - timedelta(days=59)).strftime('%Y-%m-%d')
            previous_period_end = (today - timedelta(days=30)).strftime('%Y-%m-%d')

            current_month_visits_request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date=current_period_start, end_date=current_period_end)],
                metrics=[Metric(name="sessions")],
            )
            current_month_visits_response = client.run_report(current_month_visits_request)
            current_month_users_count = 0
            if current_month_visits_response.rows:
                current_month_users_count = int(current_month_visits_response.rows[0].metric_values[0].value)

            previous_month_visits_request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date=previous_period_start, end_date=previous_period_end)],
                metrics=[Metric(name="sessions")],
            )
            previous_month_visits_response = client.run_report(previous_month_visits_request)
            previous_month_users_count = 0
            if previous_month_visits_response.rows:
                previous_month_users_count = int(previous_month_visits_response.rows[0].metric_values[0].value)

            change_percentage = 0
            if previous_month_users_count > 0:
                change_percentage = ((current_month_users_count - previous_month_users_count) / previous_month_users_count) * 100
            elif current_month_users_count > 0:
                change_percentage = 100

            data = {
                "total_users": total_users_count,
                "change_percentage": round(change_percentage, 2)
            }

            logger.info(f"Successfully fetched GA data: {data}")

            serializer = self.get_serializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching GA data: {e}", exc_info=True)
            return Response({"error": "Failed to fetch analytics data. Please check backend logs for details."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
