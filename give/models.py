from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth.models import User

from datetime import datetime

class UserException(Exception):
    """ Is thrown when there is a problem with a user, eg. if he has no profile.
    """
    pass

class DataNarcismException(ValueError):
    """ Is thrown when a user tries to give datalove to himself.
    """
    pass

class NotEnoughDataloveException(Exception):
    """ Is thrown when a user has not enough datalove to give. """
    pass

class AttributedDict(dict):
    """ To have dictionaries that act like objects (and can be easily converted
        to JSON).
    """
    def __init__(self, **entries):
        self.update(**entries)
        self.__dict__.update(entries)

class LovableObject(models.Model):
    """ An abstract object you can give datalove to.
    """
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
                    AttributedDict(url=w.url) for w in self.websites.all()
                ]
        profile_dict['resource_uri'] = self.get_api_url()
        profile_dict['give_datalove_uri'] = self.get_give_datalove_url()
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
    
    @property
    def username(self):
        return self.user.username

    def send_datalove(self, recipient, datalove=1):
        
        if datalove < 0:
            raise ValueError("datalove must be >= 0.")
        if isinstance(recipient, User):
            try:
                recipient = recipient.get_profile()
            except DataloveProfile.DoesNotExist:
                DataloveProfile.objects.create(user=recipient)
        elif isinstance(recipient, LovableObject):
            pass
        else:
            try:
                recipient = DataloveProfile.objects.get(
                        user__username=str(recipient)
                    )
            except DataloveProfile.DoesNotExist:
                raise UserException(
                        "User '%s' does not exist." % 
                        str(recipient)
                    )
        try:
            if (isinstance(recipient, DataloveProfile) and \
                    self == recipient) or \
                    (isinstance(recipient, LovableObject) and \
                    self == recipient.dataloveprofile
                ):
                raise DataNarcismException("You can not send datalove to yourself.")
        except DataloveProfile.DoesNotExist:
            pass
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
        if not isinstance(recipient, LovableItem) and \
                not isinstance(recipient, LovableObject):
            recipient.available_love += actually_spend_love
        elif isinstance(recipient, LovableObject):
            try:
                recipient.dataloveprofile.available_love += actually_spend_love
            except DataloveProfile.DoesNotExist:
                pass
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
    def get_give_datalove_url(self):
        return ('api__give_datalove', [str(self.lovableobject_ptr.id)])

    @models.permalink
    def get_api_url(self):
        return ('api__profile', [str(self.username)])
    
    @models.permalink
    def get_absolute_url(self):
        return ('profile', [str(self.username)])
    
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
        profile_dict['sender'] = self.sender.username
        try:
            profile_dict['recipient'] = self.recipient.dataloveprofile.username
        except DataloveProfile.DoesNotExist:
            profile_dict['recipient'] = self.recipient.lovableobject.id
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

