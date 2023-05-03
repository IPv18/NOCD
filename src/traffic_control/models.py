from django.db.models import F
from django.db import models
from .traffic_control import update_tc


class TCPolicy(models.Model):
    '''
    A policy is a set of iproute2/tc rules that can be applied to 
    a set of traffic aka a TCGroup or a TCProcess.
    '''
    objects = models.Manager()


    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    config      = models.JSONField()
    enabled     = models.BooleanField(default=True)
    startup     = models.BooleanField(default=False)
    created     = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created"]
        verbose_name = "Traffic Control Policy"
        verbose_name_plural = "Traffic Control Policies"


    def save(self, *args, **kwargs):
        super(TCPolicy, self).save(*args, **kwargs)    
        update_tc(self)
    
    def delete(self, *args, **kwargs):
        self.enabled = False
        self.startup = False
        update_tc(self)
        super(TCPolicy, self).delete(*args, **kwargs)
