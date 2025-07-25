from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
import os
from datetime import datetime, timedelta


from .models import JobPost
from .serializers import JobPostSerializer


class JobPostViewset(viewsets.ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer

