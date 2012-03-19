from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import unittest

import random, string, sys
from datetime import timedelta, datetime

from give.models import *

def create_user(password=None):
    if not password:
        password = randstr(30,True)
    while True:
        try:
            user = User(username=randstr(30,True),password=password)
            break
        except IntegrityError:
            pass
    user.save()
    return user

def randstr(
        length, 
        rand_len=True,
        char_set = string.ascii_uppercase + \
                   string.ascii_lowercase + \
                   string.digits
    ):
    if rand_len:
        length = random.randint(1,length)
    return ''.join(random.choice(char_set) for x in range(length))

def get_month_from_timedelta(relative_time, timedelta):
    past = relative_time - timedelta
    years = relative_time.year - past.year
    return 12*years + (relative_time.month - 
            past.month)

class TestWithAuthUser(unittest.TestCase):
    def setUp(self):
        self.sender_password = randstr(30,True)
        self.sender = create_user(self.sender_password)
    
    def tearDown(self):
        self.sender.delete()

class TestWithTwoAuthUser(TestWithAuthUser):
    def setUp(self):
        super(TestWithTwoAuthUser,self).setUp()
        self.recipient_password = randstr(30,True)
        self.recipient = create_user(self.recipient_password)
    
    def tearDown(self):
        super(TestWithTwoAuthUser,self).tearDown()
        self.recipient.delete()

class TestDataloveProfileMethods(TestWithAuthUser):
    def test_update_love_Correct(self):
        last_update = timedelta(days=random.randint(31,10*365))
        old_love = self.sender.get_profile().available_love
        self.sender.get_profile().last_love_update = datetime.now()-last_update
        months = get_month_from_timedelta(datetime.now(), last_update)
        self.sender.get_profile().update_love()
        self.assertEqual(
                old_love+months*settings.DEFAULT_UPDATE_DATALOVE, 
                self.sender.get_profile().available_love
            )
    
    def test_add_free_datalove_Correct(self):
        free_datalove = random.randint(1,sys.maxint)
        old_love = self.sender.get_profile().available_love
        self.sender.get_profile().add_free_datalove(free_datalove)
        self.assertEqual(
                old_love + free_datalove,
                self.sender.get_profile().available_love
            )
    
    def test_add_free_datalove_NoneArg(self):
        with self.assertRaises(ValueError):
            self.sender.get_profile().add_free_datalove(None)

    def test_add_free_datalove_NegativeArg(self):
        free_datalove = random.randint(-(sys.maxint-1),-1)
        with self.assertRaises(ValueError):
            self.sender.get_profile().add_free_datalove(free_datalove)
    
    def test_get_total_loverz_Correct(self):
        total_loverz = len(DataloveProfile.objects.all())
        self.assertEqual(
                total_loverz,
                DataloveProfile.get_total_loverz()
            )
    
    def test_get_profile_dict_random_selection(self):
        field_names = set([f.name for f in DataloveProfile._meta.fields])
        selection = []
        while len(selection) == 0:
            selection = [randstr(16) for _ in randstr(20,True)]
        profile_dict = self.sender.get_profile().get_profile_dict(selection)
        self.assertEqual(len(profile_dict),2)
    
    def test_get_profile_dict_valid_selection(self):
        field_names = [f.name for f in DataloveProfile._meta.fields]
        field_names.remove('user')
        field_names.remove('lovableobject_ptr')
        for _ in range(random.randint(0,len(field_names)-1)):
            random_field = random.choice(field_names)
            field_names.remove(random_field)
        profile_dict = self.sender.get_profile().get_profile_dict(field_names)
        for field in field_names:
            self.assertIsNotNone(profile_dict.pop(field))
        self.assertEqual(len(profile_dict),2)

    def test_send_datalove_Correct_RecipientUser(self):
        sender = self.sender
        recipient = create_user() 
        to_send = random.randint(1,sender.get_profile().available_love)
        before = datetime.now()
        sent = sender.get_profile().send_datalove(recipient,to_send)
        after = datetime.now()
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=sender.get_profile(),
                recipient=recipient.get_profile()
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )
    
    def test_send_datalove_Correct_RecipientProfile(self):
        sender = self.sender
        recipient = create_user()
        to_send = random.randint(1,sender.get_profile().available_love)
        before = datetime.now()
        sent = sender.get_profile().send_datalove(
                recipient.get_profile(),
                to_send
            )
        after = datetime.now()
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=sender.get_profile(),
                recipient=recipient.get_profile()
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )

    def test_send_datalove_Correct_RecipientItem(self):
        sender = self.sender
        recipient_user = create_user()
        recipient = LovableItem(creator=recipient_user.get_profile())
        recipient.save()
        to_send = random.randint(1,sender.get_profile().available_love)
        before = datetime.now()
        sent = sender.get_profile().send_datalove(recipient,to_send)
        after = datetime.now()
        self.assertEqual(to_send,sent)
        transaction = DataloveHistory.objects.get(
                sender=sender.get_profile(),
                recipient=recipient
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp >= before and 
                transaction.timestamp <= after
            )
        recipient.delete()

    @unittest.skipUnless(len(User.objects.all()) > 1, "Needs >1 users in DB.")
    def test_send_datalove_NegativeDatalove(self):
        sender = self.sender
        recipient = create_user()
        old_love = sender.get_profile().available_love
        to_send = random.randint(-(sys.maxint)-1,-1)
        with self.assertRaises(ValueError):
            sent = sender.get_profile().send_datalove(recipient,to_send)
        self.assertEqual(old_love,sender.get_profile().available_love)
    
    @unittest.skipUnless(len(User.objects.all()) > 0, "Needs a user in DB.")
    def test_send_datalove_NotExistentUser(self):
        sender = self.sender
        recipient = randstr(20) 
        old_love = sender.get_profile().available_love
        to_send = random.randint(1,sender.get_profile().available_love)
        with self.assertRaises(UserException):
            sent = sender.get_profile().send_datalove(recipient,to_send)
        self.assertEqual(old_love,sender.get_profile().available_love)

    @unittest.skipUnless(len(User.objects.all()) > 1, "Needs >1 users in DB.")
    def test_send_datalove_ToMuchLove(self):
        sender = self.sender
        recipient = create_user()
        old_love = sender.get_profile().available_love
        to_send = random.randint(
                sender.get_profile().available_love+1,
                sys.maxint
            )
        before = datetime.now()
        sent = sender.get_profile().send_datalove(recipient,to_send)
        after = datetime.now()
        self.assertNotEqual(to_send,sent)
        self.assertEqual(old_love,sent)
        self.assertEqual(sender.get_profile().available_love,0)
        transaction = DataloveHistory.objects.get(
                sender=sender.get_profile(),
                recipient=recipient.get_profile()
            )
        self.assertEqual(transaction.amount,sent)
        self.assertTrue(
                transaction.timestamp > before and 
                transaction.timestamp < after
            )
    
    @unittest.skipUnless(len(User.objects.all()) > 1, "Needs >1 users in DB.")
    def test_send_datalove_NoAvailableLove(self):
        sender = self.sender
        recipient = create_user()
        sender.get_profile().available_love = 0
        sender.get_profile().save()
        to_send = random.randint(1,sys.maxint)
        with self.assertRaises(NotEnoughDataloveException):
            sent = sender.get_profile().send_datalove(recipient,to_send)

class TestDataloveHistoryCreation(TestWithTwoAuthUser):
    def test_NoneSenderCreation(self):
        with self.assertRaises(ValueError):
            transaction = DataloveHistory(
                    sender=None,
                    recipient=self.recipient.get_profile()
                )

    def test_NoneRecipientCreation(self):
        with self.assertRaises(ValueError):
            transaction = DataloveHistory(
                    sender=self.sender.get_profile(),
                    recipient=None
                )
    
    def test_SenderAndRecipientEqualCreation(self):
        transaction = DataloveHistory(
                sender=self.sender.get_profile(),
                recipient=self.sender.get_profile()
            )
        with self.assertRaises(IntegrityError):
            transaction.save()
            

    def test_NoneAmountCreation(self):
        transaction = DataloveHistory(
                    sender=self.sender.get_profile(),
                    recipient=self.recipient.get_profile(),
                    amount=None
                )
        with self.assertRaises(IntegrityError):
            transaction.save()

    def test_NegativeAmountCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        transaction = DataloveHistory(
                sender=self.sender.get_profile(),
                recipient=self.recipient.get_profile(),
                amount=love
            )
        with self.assertRaises(IntegrityError):
            transaction.save()
    
class TestUserWebsiteCreation(TestWithAuthUser):
    def test_NoneUserCreation(self):
        url = randstr(UserWebsite.URL_LEN)
        with self.assertRaises(ValueError):
            website = UserWebsite(
                    user=None,
                    url=url
                )

    def test_NoneUrlCreation(self):
        website = UserWebsite(
                user=self.sender.get_profile(),
                url=None
            )
        with self.assertRaises(IntegrityError):
            website.save()
    
    def test_EmptyUrlCreation(self):
        website = UserWebsite(
                user=self.sender.get_profile(),
                url=''
            )
        with self.assertRaises(IntegrityError):
            website.save()

    def test_TooLongUrlCreation(self):
        url = randstr(UserWebsite.URL_LEN + 10,False)
        website = UserWebsite(
                user=self.sender.get_profile(),
                url=url
            )
        with self.assertRaises(IntegrityError):
            website.save()
    
    def test_UniquenessConstraint(self):
        url = randstr(UserWebsite.URL_LEN)
        website1 = UserWebsite(
                user=self.sender.get_profile(),
                url=url
            )
        website1.save()
        website2 = UserWebsite(
                user=self.sender.get_profile(),
                url=url
            )
        with self.assertRaises(IntegrityError):
            website2.save()

class TestLovableItemCreation(TestWithAuthUser):
    def test_NoneCreatorCreation(self):
        with self.assertRaises(ValueError):
            obj = LovableItem(creator=None)

    def test_NoneReceivedLoveCreation(self):
        obj = LovableItem(
                creator=self.sender.get_profile(),
                received_love=None
            )
        with self.assertRaises(IntegrityError):
            obj.save()

    def test_NoneReceivedLoveCreation(self):
        love = random.randint(-(sys.maxint)-1,-1)
        obj = LovableItem(
                creator=self.sender.get_profile(),
                received_love=love
            )
        with self.assertRaises(IntegrityError):
            obj.save()

