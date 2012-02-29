from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class DataloveProfile(models.Model):
    user = models.OneToOneField(
            User, 
            related_name='datalove', 
            blank=False, null=False
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
            related_name='lovable_objects'
        )
    received_love = models.PositiveIntegerField(
            blank=False, 
            null=False, 
            default=0
        )
