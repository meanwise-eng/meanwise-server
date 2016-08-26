from django.conf.urls import url
from pages import views

urlpatterns = [
    url(r'^(?P<company_slug>[-\w]+)/$', views.PageList.as_view(), name='page_list_create'),
    url(r'^(?P<company_slug>[-\w]+)/(?P<page_slug>[-\w]+)/$', views.PageDetail.as_view(),
    		name='page_detail'),
    url(r'^(?P<company_slug>[-\w]+)/leaders$', views.LeaderView.as_view(), name='leader_create'),
]
