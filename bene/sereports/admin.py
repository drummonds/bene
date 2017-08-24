from django.contrib import admin

from .models import Company, Report, RemittanceFile

admin.site.register(Company)
admin.site.register(Report)
admin.site.register(RemittanceFile)
