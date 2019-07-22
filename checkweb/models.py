from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage



class WatchUrl(models.Model):
    domain = models.URLField(max_length=120)
    description = models.TextField( max_length=500,blank=True, null=True)
    #urls = models.URLField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    active_monitor = models.BooleanField(default=True, verbose_name="Activate regular monitoring of the domain" )
    active_email_alert = models.BooleanField(default=True,verbose_name="Email is send to all users when alert triggers on this domain")
    active_alert_on_similar_ips = models.BooleanField(default=True,verbose_name="Raise an alert when IP Address changed only within same IP range")
    active_discover_urls = models.BooleanField(default=True, verbose_name="Search for http/https and www. variants as well")
    active_tor_proxy = models.BooleanField(default=False, verbose_name="Use TOR Proxy then interacting with domain")

    treshold_change_percent = models.SmallIntegerField(default=10) # percent of changed text to trigger alert



    def __str__(self):
        return self.domain

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Watched URLs"



class Snapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    watchurl = models.ForeignKey(WatchUrl, on_delete=models.CASCADE)
    my_ipaddr = models.GenericIPAddressField(blank=True, null=True)
    my_location = models.TextField(max_length=400,blank=True, null=True)

    resolved_ip = models.GenericIPAddressField(blank=True, null=True)
    http_status_first  = models.SmallIntegerField(blank=True, null=True) #fist is usually redirect 301
    http_status_last = models.SmallIntegerField(blank=True, null=True) #last status after all redirects
    access_url = models.URLField(blank=True, null=True)
    redirected_url = models.URLField(blank=True, null=True)

    html_content = models.TextField(blank=True, null=True) #unescaped full content, after all redirects
    html_dump = models.FileField(upload_to='snapshots',blank=True, null=True)
    html_dump_size = models.IntegerField(blank=True, null=True)

    def html_dump_size_readable(self, precision=2):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffixIndex = 0
        size = self.html_dump_size
        while size > 1024:
            suffixIndex += 1  # increment the index of the suffix
            size = size / 1024.0  # apply the division
        return "%.*f %s" % (precision, size, suffixes[suffixIndex])

    def __datetime__(self):
        return self.created

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Snapshots"



class Alert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message_short = models.CharField(max_length=500)
    message_verbose = models.TextField(blank=True, null=True)

    watchurl = models.ForeignKey(WatchUrl, on_delete=models.CASCADE)
    snapshot_current = models.ForeignKey(Snapshot,related_name='snapshot_current', on_delete=models.CASCADE)
    snapshot_previous = models.ForeignKey(Snapshot,related_name='snapshot_previous', on_delete=models.CASCADE)

    snapshot_diff = models.TextField(blank=True, null=True)
    acknowledge_alert = models.BooleanField(default=False)


    def __datetime__(self):
        return self.created



    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Alerts"