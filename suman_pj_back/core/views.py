from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import JobPost
from .serializers import JobPostSerializer

class JobPostViewset(viewsets.ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer