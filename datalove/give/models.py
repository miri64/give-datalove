from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth.models import User

from datetime import datetime

class DataloveProfile(models.Model):
    user = models.OneToOneField(
            User, 
            related_name='datalove', 
            blank=False, 
            null=False,
            primary_key=True,
            on_delete=models.CASCADE
        )
    available_love = models.PositiveIntegerField(
            blank=False, 
            null=False, 
            default=settings.DEFAULT_STARTING_DATALOVE
        )
    received_love = models.PositiveIntegerField(
            blank=False, 
            null=False, 
            default=0
        )

    def save(self, *args, **kwargs):
        if self.available_love < 0:
            raise IntegrityError(
                    "DataloveProfile.available_love must be >= 0"
                ) 
        if self.received_love < 0:
            raise IntegrityError(
                    "DataloveProfile.received_love must be >= 0"
                )
        super(DataloveProfile, self).save()
    
class DataloveHistory(models.Model):
    sender = models.ForeignKey(
            DataloveProfile, 
            related_name='send_history', 
            blank=False, 
            null=False
        )
    recipient = models.ForeignKey(
            DataloveProfile, 
            related_name='receive_history', 
            blank=False, 
            null=False
        )
    amount = models.PositiveIntegerField(
            blank=False, 
            null=False,
            default=1
        )
    timestamp = models.DateTimeField(
            auto_now_add=True,
            blank=False,
            null=False
        )

    def save(self, *args, **kwargs):
        if self.sender == self.recipient:
            raise IntegrityError(
                    "DataloveHistory.sender and " + 
                    "DataloveHistory.recipient must " +
                    "not be the same"
                )
        if self.amount < 0:
            raise IntegrityError(
                    "DataloveHistory.amount must be >= 0"
                )
        if not isinstance(self.timestamp,datetime):
            raise IntegrityError(
                    "DataloveHistory.timestamp must be of " +
                    "type datetime.datetime"
                )
        super(DataloveHistory, self).save(*args, **kwargs)

class UserWebsite(models.Model):
    user = models.ForeignKey(
            DataloveProfile, 
            related_name='websites', 
            blank=False, 
            null=False
        )
    website = models.URLField(
            max_length=50, 
            blank=False, 
            null=False
        )

class LovableObject(models.Model):
    creator = models.ForeignKey(
            DataloveProfile,
            related_name='lovable_objects',
            blank=False,
            null=False
        )
    received_love = models.PositiveIntegerField(
            blank=False, 
            null=False, 
            default=0
        )
    
    def save(self, *args, **kwargs):
        if self.received_love < 0:
            raise IntegrityError(
                    "LovableObject.received_love must be >= 0"
                )
        super(LovableObject,self).save(*args, **kwargs)
