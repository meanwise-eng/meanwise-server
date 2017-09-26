from django.conf.urls import url

from .views import BrandDetailsView

urlpatterns = [
    url(r'^(?P<brand_id>[0-9]+)/$', BrandDetailsView.as_view(), name='brand-details'),
]
