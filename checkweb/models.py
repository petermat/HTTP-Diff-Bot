from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage


class WatchUrl(models.Model):
    domain = models.URLField(max_length=120,help_text='Enter domain \'example.com\' and activate URL discovery checkbox below or enter exact URL to monitor. Like https://www.example.com ')
    description = models.TextField( max_length=500,blank=True, null=True, help_text='Who requested monitor? What is the story behind?')
    #urls = models.URLField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    active_monitor = models.BooleanField(default=True,
                                         verbose_name='Monitoring Active',
                                         help_text="Activate regular monitoring of the domain." )
    active_email_alert = models.BooleanField(default=True,
                                        verbose_name='Email Alers',
                                        help_text="Email is send to all active staff users when alert triggers on this domain")
    active_alert_on_similar_ips = models.BooleanField(default=True,
                                        verbose_name='IP Small Change',
                                        help_text="""Raise an alert when IP Address changed but still within same IP range.
                                        Disable to ignore small changes like 123.123.123.123 -> 123.123.123.124.""")
    active_discover_urls = models.BooleanField(default=True,
                                               verbose_name='URL Discovery',
                                               help_text="""Enter example.com and system will create http://domain.com, 
                                               http://www.domain.com, https://domain.com and https://www.domain.com  variants as well.
                                               Do not use when exact URL to watch is known, like https://something.domain.com/somasubpage/index.php 
                                               """)
    active_tor_proxy = models.BooleanField(default=False,
                                           verbose_name='TOR Proxy',
                                           help_text="""Use TOR Proxy then connecting with domain. Use when maliciocus intent is confirmed. 
                                           TOR connections are less reliable but not tracable backwards""")

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
    domain_shortname = models.URLField(max_length=120, editable=False,blank=True)

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