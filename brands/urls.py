from django.conf.urls import url

from .views import BrandDetailsView, BrandListView, BrandMembersView, BrandPostsView

urlpatterns = [
    url(r'^$', BrandListView.as_view(), name='brand-list'),
    url(r'^(?P<brand_id>[0-9]+)/$', BrandDetailsView.as_view(), name='brand-details'),
    url(r'^(?P<brand_id>[0-9]+)/members/$', BrandMembersView.as_view(), name='brand-members'),
    url(r'^(?P<brand_id>[0-9]+)/posts/$', BrandPostsView.as_view(), name='brand-posts'),
]
