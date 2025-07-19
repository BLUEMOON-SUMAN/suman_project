from rest_framework.routers import DefaultRouter
from core.views import JobPostViewset, AnalyticsDataViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'recruit', JobPostViewset, basename = 'JobPost')
router.register(r'analytics', AnalyticsDataViewSet, basename = 'analytics')

urlpatterns = router.urls
