"""
URL configuration for suman_pj_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Inquiries.urls import router as Inquery_router
from question.urls import router as faq_router
from core.urls import router as jobpost_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(Inquery_router.urls)),
    path('api/', include(faq_router.urls)),
    path('api/', include('user.urls')),
    path('api/', include(jobpost_router.urls)),
]
