from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import FAQ
from .serializers import FAQserializer

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQserializer
