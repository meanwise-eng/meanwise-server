from django.contrib import admin
# from django.contrib.admin import AdminSite
# from django.utils.translation import ugettext_lazy

# Register your models here.
from .models import Company, EmailConfirmation, CompanyProfile, CompanyLocation, CompanyCulture

class CompanyModelAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'verified')
    list_editable = ['verified']
    search_fields = ['company_name']

class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_description', 'company_size')

class CompanyLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lon', 'lat', 'isHQ')
    list_editable = ['isHQ']

class CompanyCultureAdmin(admin.ModelAdmin):
    list_display = ('influence', 'adventurous', 'achievement',
                    'col_ind', 'openness', 'pub_vs_priv')

class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('company', 'email', 'confirmed')
    list_filter = ['confirmed']
    search_fields = ['company']

admin.site.site_header = 'meanwise'
admin.site.register(Company, CompanyModelAdmin)
admin.site.register(CompanyProfile, CompanyProfileAdmin)
admin.site.register(CompanyLocation, CompanyLocationAdmin)
admin.site.register(CompanyCulture, CompanyCultureAdmin)
admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
