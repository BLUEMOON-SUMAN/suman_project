from rest_framework.routers import DefaultRouter
from .views import JobPostViewset
from django.urls import path, include

router = DefaultRouter()
router.register(r'recruit', JobPostViewset, basename = 'JobPost')

urlpatterns = router.urls
