from django.db import models
from django.contrib.auth.models import User

class DataloveProfile(models.Model):
    user = models.OneToOneField(User,related_name='datalove')
    available_love = models.PositiveIntegerField(blank=False, null=False, default=0)
    received_love = models.PositiveIntegerField(blank=False, null=False, default=0)

class DataloveHistory(models.Model):
    sender = models.ForeignKey(DataloveProfile, related_name='send_history')
    recipient = models.ForeignKey(DataloveProfile, related_name='receive_history')
    amount = models.PositiveIntegerField(blank=False, null=False)

class UserWebsite(models.Model):
    user = models.ForeignKey(DataloveProfile,related_name='websites')
    website = models.URLField(max_length=50, blank=False, null=False)
