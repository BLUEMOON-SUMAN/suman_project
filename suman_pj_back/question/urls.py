from rest_framework.routers import DefaultRouter
from question.views import FAQViewSet

router = DefaultRouter()
router.register(r'faqs', FAQViewSet, basename = 'faq')

urlpatterns = router.urls