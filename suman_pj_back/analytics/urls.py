from rest_framework.routers import DefaultRouter
from .views import AnalyticsDataViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'analytics', AnalyticsDataViewSet, basename = 'analytics')

urlpatterns = router.urls
