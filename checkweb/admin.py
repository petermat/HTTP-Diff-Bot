from django.contrib import admin

from django.utils.html import format_html

from .models import WatchUrl,Snapshot, Alert

### MASS ACTIONS for admin interface ###
def activate_active_monitor(modeladmin, request, queryset):
    queryset.update(active_monitor=True)
activate_active_monitor.short_description = "Activate monitoring"
def deactivate_active_monitor(modeladmin, request, queryset):
    queryset.update(active_monitor=False)
deactivate_active_monitor.short_description = "Disable monitoring"

def activate_email_alerting(modeladmin, request, queryset):
    queryset.update(active_email_alert=True)
activate_email_alerting.short_description = "Activate Email Alerting"
def deactivate_email_alerting(modeladmin, request, queryset):
    queryset.update(active_email_alert=False)
deactivate_email_alerting.short_description = "Disable Email Alerting"



### DATABASE  DEFINITION ###
class watchUrlAdmin(admin.ModelAdmin):
    list_display = ('domain','active_monitor','active_email_alert', 'active_discover_urls','active_tor_proxy',
                    'description', 'created', 'updated')
    actions = [activate_active_monitor, deactivate_active_monitor,activate_email_alerting,deactivate_email_alerting]
    list_filter = ('active_monitor','active_email_alert','active_tor_proxy')

admin.site.register(WatchUrl, watchUrlAdmin)


class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('created','access_url','redirected_url','html_dump','html_dump_size_readable',
                    'http_status_first','http_status_last','resolved_ip','my_ipaddr','my_location')
    list_filter= ('access_url',)
admin.site.register(Snapshot, SnapshotAdmin)


class AlertAdmin(admin.ModelAdmin):
    def content_diff(self, obj):
        if 'Change in content ' in obj.message_short:
        #return '<a href="%s">%s</a>' % (obj.snapshot_current.id, "aaaa")
            return format_html("<a href='../../../checkweb/content_diff?id={id2}'>{id} vs {id2}</a>",
                               id2=obj.snapshot_current.id, id=obj.snapshot_previous.id)
        else:
            return format_html('n/a')
    content_diff.mark_safe = True

    list_display = ('created','content_diff','watchurl','message_short','acknowledge_alert')
    list_filter = ('watchurl',)
admin.site.register(Alert, AlertAdmin)