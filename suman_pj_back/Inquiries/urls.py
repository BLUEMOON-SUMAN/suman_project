from rest_framework.routers import DefaultRouter
from Inquiries.views import InquiryViewSet

router = DefaultRouter()
router.register(r'Inquiries', InquiryViewSet, basename='Inquiry')

urlpatterns = router.urls