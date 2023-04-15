from django.db import models

class NotificationInfo(models.Model):
    type = models.CharField(max_length=31)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message