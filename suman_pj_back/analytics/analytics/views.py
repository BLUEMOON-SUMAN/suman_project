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

import logging
logger = logging.getLogger(__name__) # 이제 이 로거는 analytics 앱의 로그를 남길 것입니다.


# 이전 views.py에서 AnalyticsDataSerializer를 잘라내어 여기에 붙여넣습니다.
class AnalyticsDataSerializer(serializers.Serializer):
    total_users = serializers.IntegerField(read_only=True)
    change_percentage = serializers.FloatField(read_only=True)

# Google Analytics Data API를 통해 방문자 통계 데이터를 제공하는 ViewSet
class AnalyticsDataViewSet(GenericViewSet):
    serializer_class = AnalyticsDataSerializer
    queryset = [] # 모델과 연결되지 않으므로 더미로 둡니다.

    def list(self, request, *args, **kwargs):
        try:
            # 서비스 계정 인증 정보를 로드합니다.
            # 이 코드는 suman_project/suman_pj_back/ga_service_account_key.json 을 기대합니다.
            SERVICE_ACCOUNT_KEY_FILE = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ga_service_account_key.json'
            )
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY_FILE,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
            client = BetaAnalyticsDataClient(credentials=credentials)

            GA4_PROPERTY_ID = 497127177 # 실제 웹사이트의 GA4 Property ID로 변경해야 합니다.

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