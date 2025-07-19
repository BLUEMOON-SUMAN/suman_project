from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
import os
from datetime import datetime, timedelta
from rest_framework import serializers

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account


from .models import JobPost
from .serializers import JobPostSerializer
import logging
logger = logging.getLogger(__name__) # __name__ 대신 'analytics_app' (settings.py의 로거 이름)으로 할 수도 있습니다.

class JobPostViewset(viewsets.ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer


class AnalyticsDataSerializer(serializers.Serializer):
    total_users = serializers.IntegerField(read_only=True)
    change_percentage = serializers.FloatField(read_only=True)

#Google Analytics Data API를 통해 방문자 통계 데이터를 제공하는 ViewSet
#`list` 액션(GET 요청)을 통해 총 방문자 수와 한 달 전 대비 방문자 수를 조회
class AnalyticsDataViewSet(GenericViewSet):
    serializer_class = AnalyticsDataSerializer
    # queryset은 모델과 연결될 때 의미가 있지만, 여기서는 더미로 설정합니다.
    # 실제로 이 쿼리셋은 사용되지 않음
    queryset = []

    def list(self, request, *args, **kwargs):
        try:
            # 서비스 계정 인증 정보를 로드합니다.
            # 'ga_service_account_key.json' 파일 경로를 프로젝트에 맞게 확인해주세요.
            SERVICE_ACCOUNT_KEY_FILE = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ga_service_account_key.json'
            )
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY_FILE,
                scopes=['https://www.googleapis.com/auth/analytics.readonly'] # Google Analytics 읽기 전용 권한
            )
            client = BetaAnalyticsDataClient(credentials=credentials)

            # Google Analytics 4 (GA4) 속성 ID입니다.
            # 실제 웹사이트의 GA4 Property ID로 변경해야 합니다.
            GA4_PROPERTY_ID = 497127177

            # --- 1. 현재까지의 총 방문 횟수 (세션 수) 조회 ---
            # 'totalUsers' 대신 'sessions' 측정 항목 사용
            total_visits_request = RunReportRequest( # 변수명 변경: total_users_request -> total_visits_request
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date="2020-01-01", end_date="today")],
                metrics=[Metric(name="sessions")], # <--- 핵심 변경: totalUsers -> sessions
            )
            total_visits_response = client.run_report(total_visits_request) # 변수명 변경
            total_users_count = 0 # 변수명 변경: total_users -> total_users_count (실제로는 세션 수)
            if total_visits_response.rows:
                total_users_count = int(total_visits_response.rows[0].metric_values[0].value)

            # --- 2. 지난 한 달 대비 방문 횟수 (세션 수) 변화율 계산 ---
            today = datetime.now()
            # 현재 30일 기간: 오늘로부터 29일 전 ~ 오늘
            current_period_start = (today - timedelta(days=29)).strftime('%Y-%m-%d')
            current_period_end = today.strftime('%Y-%m-%d')
            # 이전 30일 기간: 오늘로부터 59일 전 ~ 30일 전
            previous_period_start = (today - timedelta(days=59)).strftime('%Y-%m-%d')
            previous_period_end = (today - timedelta(days=30)).strftime('%Y-%m-%d')

            # 현재 30일간의 세션 수 조회
            current_month_visits_request = RunReportRequest( # 변수명 변경
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date=current_period_start, end_date=current_period_end)],
                metrics=[Metric(name="sessions")], # <--- 핵심 변경: activeUsers -> sessions
            )
            current_month_visits_response = client.run_report(current_month_visits_request) # 변수명 변경
            current_month_users_count = 0 # 변수명 변경 (실제로는 세션 수)
            if current_month_visits_response.rows:
                current_month_users_count = int(current_month_visits_response.rows[0].metric_values[0].value)

            # 이전 30일간의 세션 수 조회
            previous_month_visits_request = RunReportRequest( # 변수명 변경
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date=previous_period_start, end_date=previous_period_end)],
                metrics=[Metric(name="sessions")], # <--- 핵심 변경: activeUsers -> sessions
            )
            previous_month_visits_response = client.run_report(previous_month_visits_request) # 변수명 변경
            previous_month_users_count = 0 # 변수명 변경 (실제로는 세션 수)
            if previous_month_visits_response.rows:
                previous_month_users_count = int(previous_month_visits_response.rows[0].metric_values[0].value)

            # 변화율 계산 (이제 '세션 수' 기반)
            change_percentage = 0
            if previous_month_users_count > 0:
                change_percentage = ((current_month_users_count - previous_month_users_count) / previous_month_users_count) * 100
            elif current_month_users_count > 0:
                # 이전 기간 세션이 0인데 현재 기간 세션이 있다면 100% 증가로 간주합니다.
                change_percentage = 100

            # --- 프론트엔드에 전달할 최종 데이터 구성 ---
            # AnalyticsDataSerializer에 정의된 필드명(`total_users`, `change_percentage`)은 유지합니다.
            data = {
                "total_users": total_users_count, # 이제 이 값은 '총 세션 수'를 나타냅니다.
                "change_percentage": round(change_percentage, 2) # 이제 이 값은 '세션 수 증감률'을 나타냅니다.
            }

            logger.info(f"Successfully fetched GA data: {data}")

            # DRF Serializer를 사용하여 데이터 직렬화
            serializer = self.get_serializer(data)
            # serializer.is_valid(raise_exception=True) # GET 요청에서는 보통 유효성 검사가 필요 없습니다.

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # 예외 발생 시 에러 로깅 및 적절한 에러 응답 반환
            logger.error(f"Error fetching GA data: {e}", exc_info=True)
            return Response({"error": "Failed to fetch analytics data. Please check backend logs for details."},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
