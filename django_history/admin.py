from django.contrib import admin
from django_history.models import ChangeLog

class ChangeLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'change_time'
    list_filter = ['change_time',  'change_type', 'content_type']
    
    fieldsets = (
        ('Meta info', {'fields': ('change_time', 'content_type', 'object_id',
                                  'user', 'revision', 'revert_from')}),
       ('Object', {'fields': ('object',)}),
    )

    list_display = ('__str__', 'user', 'change_type', 'content_type', 
                    'change_time', 'revision', 'revert_from')

admin.site.register(ChangeLog, ChangeLogAdmin )
