from django.conf.urls import url, include
from company import api, views

urlpatterns = [
    url(r'^company/$', api.CompanyList.as_view(),
        name='company_list'),
    url(r'^company/(?P<slug>[-\w]+)/$', api.CompanyDetail.as_view(),
        name='company_detail'),
    url(r'^(?P<slug>[-\w]+)/$', api.CompanyProfileCRUD.as_view(),
        name='profile_crud'),
    url(r'^(?P<slug>[-\w]+)/locations/$', api.CompanyLocationCRUD.as_view(),
        name='location_crud'),
    url(r'^signup/$', views.CreateCompany,
        name='company_signup'),
    url(r'^confirm/(?P<token>[a-zA-Z0-9_.-]+)/$', views.ConfirmCompany,
        name='confirm_company'),
    url(r'^resendconfirmation/(?P<email>[a-zA-Z0-9_.@]+)/$',
        views.ResendConfirmationEmail, name='resend_email_confirmation')
]

#  url(r'^signup/$', views.CreateCompany, name='company_signup')
