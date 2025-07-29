from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAdminUser
import django_filters.rest_framework

from .models import FAQ, Category
from .serializers import FAQserializer


class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQserializer

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_published']
    search_fields = ['question', 'answer']
    ordering_fields = ['id', 'category']    

    def get_queryset(self):
        queryset = FAQ.objects.select_related('category')

        if self.request.user.is_authenticated and self.request.user.is_staff :
            return queryset.order_by('category__order','category__name', 'id')
        else :
            return queryset.filter(is_published = True).order_by('category__order','category__name','id')
        
    def get_permissions(self) :
        if self.request.method == 'GET' :
            self.permission_classes = [AllowAny]
        else :
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
