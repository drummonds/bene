from django.contrib import admin

from .models import ContactGroup, Contact, Item, Invoice

admin.site.register(ContactGroup)
admin.site.register(Contact)
admin.site.register(Item)
admin.site.register(Invoice)
