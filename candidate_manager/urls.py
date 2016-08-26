from django.conf.urls import url, include

from .views import view_candidate

urlpatterns = [
	 url(r'(?P<company_slug>[-\w]+)/(?P<job_slug>[-\w]+)/view_applicants/$', view_candidate),
]