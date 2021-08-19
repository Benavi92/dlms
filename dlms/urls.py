"""dlms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import include
from django.urls import path, re_path
from mailer.views import email_lists
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', email_lists, name='main'),
    path('admin/', admin.site.urls),
    path('mails/', include('mailer.urls')),
    path('wiki/', include('wiki.urls')),
    path(r'^api-auth/', include('rest_framework.urls')),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),
    path("api/", include('restapi.urls')),
    path("dfs/", include('dfs_exch.urls'))

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
