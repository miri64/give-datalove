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
        super(DataloveHistory, self).save(*args, **kwargs)

class UserWebsite(models.Model):
    URL_LEN = 50
    user = models.ForeignKey(
            DataloveProfile, 
            related_name='websites', 
            blank=False, 
            null=False
        )
    url = models.URLField(
            max_length=URL_LEN, 
            blank=False, 
            null=False
        )
    
    class Meta:
        unique_together = ("user","url")

    def save(self, *args, **kwargs):
        if self.url != None:
            if len(self.url) == 0:
                raise IntegrityError(
                        "UserWebsite.url may not be an empty " +
                        "string."
                    )
            if len(self.url) > UserWebsite.URL_LEN:
                raise IntegrityError(
                        "UserWebsite.url may not be longer " +
                        "then %d charactes" % UserWebsite.URL_LEN
                    )
        super(UserWebsite,self).save(*args, **kwargs)

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


## Tests
from django.utils import unittest

import random, string, sys

def create_user():
    username = 'test'
    if len(User.objects.filter(username=username)) > 0:
        running_number = 0
        username = "test%03d" % running_number
        while len(User.objects.filter(username=username)) > 0:
            running_number += 1
            username = "test%03d" % running_number
    user = User(username=username,password=username)
    user.save()
    return username,user

def create_profile(user):
    return DataloveProfile.objects.create(user=user) 

def randstr(
        length, 
        rand_len=True,
        char_set = string.ascii_uppercase + \
                   string.ascii_lowercase + \
                   string.digits + ':./%?#&\\'
    ):
    if rand_len:
        length = random.randint(1,length)
    return ''.join(random.choice(char_set) for x in range(length))

class TestUserProfileCreation(unittest.TestCase):
    def setUp(self):
        _, self.user = create_user()
    
    def test_NoneUserProfileCreation(self):
        with self.assertRaises(ValueError):
            profile = DataloveProfile(user=None)
    
    def test_NoneAvailableLoveCreation(self):
        profile = DataloveProfile(
                user=self.user,
                available_love=None
            )
        with self.assertRaises(IntegrityError):
            profile.save()

    def test_NoneReceivedLoveCreation(self):
        profile = DataloveProfile(
                user=self.user, 
                received_love=None
            )
        with self.assertRaises(IntegrityError):
            profile.save()
    
    def test_NegativeAvailableLoveCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        profile = DataloveProfile(
                user=self.user, 
                available_love=love
            )
        with self.assertRaises(IntegrityError):
            profile.save()

    def test_NegativeReceivedLoveCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        profile = DataloveProfile(
                user=self.user, 
                available_love=love
            )
        with self.assertRaises(IntegrityError):
            profile.save()

    def tearDown(self):
        self.user.delete()

class TestDataloveHistoryCreation(unittest.TestCase):
    def setUp(self):
        _, self.user1 = create_user()
        self.profile1 = create_profile(self.user1)
        _, self.user2 = create_user()
        self.profile2 = create_profile(self.user2)
    
    def test_NoneSenderCreation(self):
        with self.assertRaises(ValueError):
            transaction = DataloveHistory(
                    sender=None,
                    recipient=self.profile2
                )

    def test_NoneRecipientCreation(self):
        with self.assertRaises(ValueError):
            transaction = DataloveHistory(
                    sender=self.profile1,
                    recipient=None
                )
    
    def test_SenderAndRecipientEqualCreation(self):
        transaction = DataloveHistory(
                sender=self.profile1,
                recipient=self.profile1
            )
        with self.assertRaises(IntegrityError):
            transaction.save()
            

    def test_NoneAmountCreation(self):
        transaction = DataloveHistory(
                    sender=self.profile1,
                    recipient=self.profile2,
                    amount=None
                )
        with self.assertRaises(IntegrityError):
            transaction.save()

    def test_NegativeAmountCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        transaction = DataloveHistory(
                sender=self.profile1,
                recipient=self.profile2,
                amount=love
            )
        with self.assertRaises(IntegrityError):
            transaction.save()
    
    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

class TestUserWebsiteCreation(unittest.TestCase):
    def setUp(self):
        _, self.user = create_user()
        self.profile = create_profile(self.user)
    
    def test_NoneUserCreation(self):
        url = randstr(UserWebsite.URL_LEN)
        with self.assertRaises(ValueError):
            website = UserWebsite(
                    user=None,
                    url=url
                )

    def test_NoneUrlCreation(self):
        website = UserWebsite(
                user=self.profile,
                url=None
            )
        with self.assertRaises(IntegrityError):
            website.save()
    
    def test_EmptyUrlCreation(self):
        website = UserWebsite(
                user=self.profile,
                url=''
            )
        with self.assertRaises(IntegrityError):
            website.save()

    def test_TooLongUrlCreation(self):
        url = randstr(UserWebsite.URL_LEN + 10,False)
        website = UserWebsite(
                user=self.profile,
                url=url
            )
        with self.assertRaises(IntegrityError):
            website.save()
    
    def test_UniquenessConstraint(self):
        url = randstr(UserWebsite.URL_LEN)
        website1 = UserWebsite(
                user=self.profile,
                url=url
            )
        website1.save()
        website2 = UserWebsite(
                user=self.profile,
                url=url
            )
        with self.assertRaises(IntegrityError):
            website2.save()

    def tearDown(self):
        self.user.delete()

class TestLovableObjectCreation(unittest.TestCase):
    def setUp(self):
        _, self.user = create_user()
        self.profile = create_profile(self.user)
    
    def test_NoneCreatorCreation(self):
        with self.assertRaises(ValueError):
            obj = LovableObject(creator=None)

    def test_NoneReceivedLoveCreation(self):
        obj = LovableObject(
                creator=self.profile,
                received_love=None
            )
        with self.assertRaises(IntegrityError):
            obj.save()

    def test_NoneReceivedLoveCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        obj = LovableObject(
                creator=self.profile,
                received_love=love
            )
        with self.assertRaises(IntegrityError):
            obj.save()

    def tearDown(self):
        self.user.delete()

