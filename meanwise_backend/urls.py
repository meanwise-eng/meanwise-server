"""meanwise_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

#from api_v3 import urls as api_v3_urls
from api_v4 import urls as api_v4_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^api/v3/', include(api_v3_urls)),
    url(r'^api/v4/', include(api_v4_urls)),
    url(r'^health-check/', include('health_check.urls')),
]

if settings.DEBUG:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
