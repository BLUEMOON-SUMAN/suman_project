from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from django.urls import path
from .views import TokenObtainPairView
from .views import OnlyAuthenticatedUserView

urlpatterns = [
    # path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('authonly/', OnlyAuthenticatedUserView.as_view(), name='authonly_test'),
]




