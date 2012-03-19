from django.contrib.auth.models import User
from django.utils import unittest

import random, string, sys
from datetime import timedelta, datetime

from give.models import *

def create_user():
    username = 'test'
    if len(User.objects.filter(username=username)) > 0:
        running_number = 0
        username = "test%03d" % running_number
        while len(User.objects.filter(username=username)) > 0:
            running_number += 1
            username = "test%03d" % running_number
    user = User(username=username)
    user.set_password(username)
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
        to_send = random.randint(1,self.user.get_profile().available_love)
        before = datetime.now()
        sent = self.user.get_profile().send_datalove(recipient,to_send)
        after = datetime.now()
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=self.user.get_profile(),
                recipient=recipient
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp >= before and 
                transaction.timestamp <= after
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

