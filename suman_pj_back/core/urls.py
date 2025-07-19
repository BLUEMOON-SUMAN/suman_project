from rest_framework.routers import DefaultRouter
from core.views import JobPostViewset

router = DefaultRouter()
router.register(r'recruit', JobPostViewset, basename = 'JobPost')

urlpatterns = router.urls