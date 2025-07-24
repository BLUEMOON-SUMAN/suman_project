from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Inquiry
from .serializers import Inquiryserializer

class InquiryViewSet(viewsets.ModelViewSet) :
    queryset = Inquiry.objects.all()
    serializer_class = Inquiryserializer

def get_permissions(self) :
    if self.request.method == 'POST' :
        self.permission_classes = [AllowAny]
    else :
        self.permission_classes = [IsAdminUser]
    return super().get_permissions()
