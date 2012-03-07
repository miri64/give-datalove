from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth.models import User

from datetime import datetime

class UserException(Exception):
    pass

class NotEnoughDataloveException(Exception):
    pass

class AttributedDict(dict):
    def __init__(self, **entries):
        self.update(**entries)
        self.__dict__.update(entries)

class LovableObject(models.Model):
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
    
    def __str__(self):
        result = "("
        for f in self._meta.fields:
            result += f.name + "=" + f.value_to_string(self) + ","
        return result[:-1]+")"

class DataloveProfile(LovableObject):
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
    last_love_update = models.DateField(
            blank=False,
            null=False,
            auto_now=True,
            auto_now_add=True
        )

    def save(self, *args, **kwargs):
        if self.available_love < 0:
            raise IntegrityError(
                    "DataloveProfile.available_love must be >= 0"
                ) 
        super(DataloveProfile, self).save(*args, **kwargs)

    def add_free_datalove(self, datalove):
        if datalove < 0:
            raise ValueError("Free datalove must be >= 0.")
        self.available_love += datalove
    
    def get_profile_dict(self, selection = None):
        profile_dict = dict()
        if selection == None:
            selection = [f.name for f in self._meta.fields]
            selection.remove('user')
            selection.remove('lovableobject_ptr')
            selection.remove('id')
            selection += [f.name for f in self.user._meta.fields]
            selection.append('websites')
        for key in set(selection) & set(self.__dict__.keys()):
            profile_dict[key] = self.__dict__[key]
        for key in set(selection) & set(self.user.__dict__.keys()):
            profile_dict[key] = self.user.__dict__[key]
        if 'websites' in selection:
            profile_dict['website'] = [
                    AttributedDict(url=w) for w in self.websites.all()
                ]
        return AttributedDict(**profile_dict)
    
    @staticmethod
    def get_total_loverz():
        return len(DataloveProfile.objects.all())

    @staticmethod
    def get_random_profile():
        profiles = DataloveProfile.objects.order_by('?')
        if len(profiles) > 0:
            return profiles[0]
        else:
            return None

    def send_datalove(self, recipient, datalove=1):
        if datalove < 0:
            raise ValueError("datalove must be >= 0.")
        if isinstance(recipient, User):
            try:
                recipient = recipient.get_profile()
            except DataloveProfile.DoesNotExist:
                raise UserException(
                        "User '%s' has no datalove profile." % 
                        recipient.username
                    )
        elif isinstance(recipient, LovableObject):
            pass
        else:
            try:
                recipient = DataloveProfile.objects.get(
                        user__username=str(recipient)
                    )
            except User.DoesNotExist:
                raise UserException(
                        "User '%s' does not exist." % 
                        str(recipient)
                    )
        if self == recipient:
            raise IntegrityError("You can not send datalove to yourself.")
        self.update_love()
        if self.available_love == 0:
            raise NotEnoughDataloveException(
                    "%s does not have enough datalove." % 
                    self.user.username
                )
        actually_spend_love = min(
                self.available_love,
                datalove
            )
        self.available_love -= actually_spend_love
        recipient.received_love += actually_spend_love
        if not isinstance(recipient, LovableItem):
            recipient.available_love += actually_spend_love
        transaction = DataloveHistory(
                sender=self,
                recipient=recipient,
                amount=actually_spend_love
            )
        transaction.save()
        recipient.save()
        self.save()
        return actually_spend_love

    def update_love(self):
        current_time = datetime.today()
        years = current_time.year - self.last_love_update.year
        months = 12*years + (current_time.month - 
                self.last_love_update.month)

        if (months > 0):
            self.available_love += months * settings.DEFAULT_UPDATE_DATALOVE
            self.save()
    
    @models.permalink
    def get_api_url(self):
        return ('api__profile', [str(self.user.id)])
    
    @models.permalink
    def get_absolute_url(self):
        return ('profile', [str(self.user.username)])
    
    def __str__(self):
        result = "("
        for f in self._meta.fields:
            result += f.name + "=" + f.value_to_string(self) + ","
        return result[:-1]+")"

def _create_user_profile(sender, instance, created, **kwargs):
    if created:
        DataloveProfile.objects.create(user=instance)

models.signals.post_save.connect(_create_user_profile, sender=User)

class DataloveHistory(models.Model):
    sender = models.ForeignKey(
            DataloveProfile, 
            related_name='send_history', 
            blank=False, 
            null=False
        )
    recipient = models.ForeignKey(
            LovableObject, 
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
    
    class Meta:
        ordering = ['-timestamp']
    
    def get_history_dict(self, selection=None):
        profile_dict = dict()
        if selection == None:
            selection = [f.name for f in self._meta.fields]
            selection.remove('id')
        for key in set(selection) & set(self.__dict__.keys()):
            profile_dict[key] = str(self.__dict__[key])
        return AttributedDict(**profile_dict)

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
    
    def __str__(self):
        result = "("
        for f in self._meta.fields:
            result += f.name + "=" + f.value_to_string(self) + ","
        return result[:-1]+")"

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
    
    def __str__(self):
        result = "("
        for f in self._meta.fields:
            result += f.name + "=" + f.value_to_string(self) + ","
        return result[:-1]+")"

class LovableItem(LovableObject):
    creator = models.ForeignKey(
            DataloveProfile,
            related_name='lovable_objects',
            blank=False,
            null=False
        )
    
    def __str__(self):
        result = "("
        for f in self._meta.fields:
            result += f.name + "=" + f.value_to_string(self) + ","
        return result[:-1]+")"


## Tests
from django.utils import unittest

import random, string, sys
from datetime import timedelta, datetime

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

class TestDataloveProfileMethods(unittest.TestCase):
    def setUp(self):
        _,self.user = create_user()

    def test_update_love_Correct(self):
        year = timedelta(days=365)
        old_love = self.user.get_profile().available_love
        self.user.get_profile().last_love_update -= year
        self.user.get_profile().update_love()
        try:
            self.assertEqual(
                    old_love+11*settings.DEFAULT_UPDATE_DATALOVE, 
                    self.user.get_profile().available_love
                )
        except AssertionError:
            self.assertEqual(
                    old_love+12*settings.DEFAULT_UPDATE_DATALOVE, 
                    self.user.get_profile().available_love
                )
    
    def test_add_free_datalove_Correct(self):
        free_datalove = random.randint(1,sys.maxint)
        old_love = self.user.get_profile().available_love
        self.user.get_profile().add_free_datalove(free_datalove)
        self.assertEqual(
                old_love + free_datalove,
                self.user.get_profile().available_love
            )
    
    def test_add_free_datalove_NoneArg(self):
        with self.assertRaises(ValueError):
            self.user.get_profile().add_free_datalove(None)

    def test_add_free_datalove_NegativeArg(self):
        free_datalove = random.randint(-(sys.maxint-1),-1)
        with self.assertRaises(ValueError):
            self.user.get_profile().add_free_datalove(free_datalove)
    
    def test_get_total_loverz_Correct(self):
        total_loverz = len(DataloveProfile.objects.all())
        self.assertEqual(
                total_loverz,
                DataloveProfile.get_total_loverz()
            )
    
    def test_send_datalove_Correct_RecipientUser(self):
        _,recipient = create_user()
        to_send = random.randint(1,self.user.get_profile().available_love)
        before = datetime.now()
        sent = self.user.get_profile().send_datalove(recipient,to_send)
        after = datetime.now()
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=self.user.get_profile(),
                recipient=recipient.get_profile()
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )
        recipient.delete()
    
    def test_send_datalove_Correct_RecipientProfile(self):
        _,recipient = create_user()
        to_send = random.randint(1,self.user.get_profile().available_love)
        before = datetime.now()
        sent = self.user.get_profile().send_datalove(
                recipient.get_profile(),
                to_send
            )
        after = datetime.now()
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=self.user.get_profile(),
                recipient=recipient.get_profile()
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )
        recipient.delete()

    def test_send_datalove_Correct_RecipientItem(self):
        recipient = LovableItem(creator=self.user.get_profile())
        recipient.save()
        before = datetime.now()
        to_send = random.randint(1,self.user.get_profile().available_love)
        after = datetime.now()
        sent = self.user.get_profile().send_datalove(recipient,to_send)
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=self.user.get_profile(),
                recipient=recipient
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )
        recipient.delete()

    def test_send_datalove_NegativeDatalove(self):
        _,recipient = create_user()
        old_love = self.user.get_profile().available_love
        to_send = random.randint(-(sys.maxint)-1,-1)
        with self.assertRaises(ValueError):
            sent = self.user.get_profile().send_datalove(recipient,to_send)
        self.assertEqual(old_love,self.user.get_profile().available_love)
        recipient.delete()
    
    def test_send_datalove_NotExistentUser(self):
        recipient = randstr(20) 
        old_love = self.user.get_profile().available_love
        to_send = random.randint(1,self.user.get_profile().available_love)
        with self.assertRaises(UserException):
            sent = self.user.get_profile().send_datalove(recipient,to_send)
        self.assertEqual(old_love,self.user.get_profile().available_love)

    def test_send_datalove_ToMuchLove(self):
        _,recipient = create_user()
        old_love = self.user.get_profile().available_love
        to_send = random.randint(
                self.user.get_profile().available_love+1,
                sys.maxint
            )
        before = datetime.now()
        sent = self.user.get_profile().send_datalove(recipient,to_send)
        after = datetime.now()
        self.assertNotEqual(to_send,sent)
        self.assertEqual(old_love,sent)
        self.assertEqual(self.user.get_profile().available_love,0)
        transaction = DataloveHistory.objects.get(
                sender=self.user.get_profile(),
                recipient=recipient.get_profile()
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )
        recipient.delete()
    
    def test_send_datalove_NoAvailableLove(self):
        _,recipient = create_user()
        self.user.get_profile().available_love = 0
        self.user.get_profile().save()
        to_send = random.randint(1,sys.maxint)
        with self.assertRaises(NotEnoughDataloveException):
            sent = self.user.get_profile().send_datalove(recipient,to_send)

    def tearDown(self):
        self.user.delete()

class TestDataloveHistoryCreation(unittest.TestCase):
    def setUp(self):
        _, self.user1 = create_user()
        _, self.user2 = create_user()
    
    def test_NoneSenderCreation(self):
        with self.assertRaises(ValueError):
            transaction = DataloveHistory(
                    sender=None,
                    recipient=self.user2.get_profile()
                )

    def test_NoneRecipientCreation(self):
        with self.assertRaises(ValueError):
            transaction = DataloveHistory(
                    sender=self.user1.get_profile(),
                    recipient=None
                )
    
    def test_SenderAndRecipientEqualCreation(self):
        transaction = DataloveHistory(
                sender=self.user1.get_profile(),
                recipient=self.user1.get_profile()
            )
        with self.assertRaises(IntegrityError):
            transaction.save()
            

    def test_NoneAmountCreation(self):
        transaction = DataloveHistory(
                    sender=self.user1.get_profile(),
                    recipient=self.user2.get_profile(),
                    amount=None
                )
        with self.assertRaises(IntegrityError):
            transaction.save()

    def test_NegativeAmountCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        transaction = DataloveHistory(
                sender=self.user1.get_profile(),
                recipient=self.user2.get_profile(),
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
    
    def test_NoneUserCreation(self):
        url = randstr(UserWebsite.URL_LEN)
        with self.assertRaises(ValueError):
            website = UserWebsite(
                    user=None,
                    url=url
                )

    def test_NoneUrlCreation(self):
        website = UserWebsite(
                user=self.user.get_profile(),
                url=None
            )
        with self.assertRaises(IntegrityError):
            website.save()
    
    def test_EmptyUrlCreation(self):
        website = UserWebsite(
                user=self.user.get_profile(),
                url=''
            )
        with self.assertRaises(IntegrityError):
            website.save()

    def test_TooLongUrlCreation(self):
        url = randstr(UserWebsite.URL_LEN + 10,False)
        website = UserWebsite(
                user=self.user.get_profile(),
                url=url
            )
        with self.assertRaises(IntegrityError):
            website.save()
    
    def test_UniquenessConstraint(self):
        url = randstr(UserWebsite.URL_LEN)
        website1 = UserWebsite(
                user=self.user.get_profile(),
                url=url
            )
        website1.save()
        website2 = UserWebsite(
                user=self.user.get_profile(),
                url=url
            )
        with self.assertRaises(IntegrityError):
            website2.save()

    def tearDown(self):
        self.user.delete()

class TestLovableItemCreation(unittest.TestCase):
    def setUp(self):
        _, self.user = create_user()
    
    def test_NoneCreatorCreation(self):
        with self.assertRaises(ValueError):
            obj = LovableItem(creator=None)

    def test_NoneReceivedLoveCreation(self):
        obj = LovableItem(
                creator=self.user.get_profile(),
                received_love=None
            )
        with self.assertRaises(IntegrityError):
            obj.save()

    def test_NoneReceivedLoveCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        obj = LovableItem(
                creator=self.user.get_profile(),
                received_love=love
            )
        with self.assertRaises(IntegrityError):
            obj.save()

    def tearDown(self):
        self.user.delete()

