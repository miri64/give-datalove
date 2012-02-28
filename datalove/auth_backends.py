# Source: http://stackoverflow.com/questions/8190642/migrating-a-password-field-to-django 
from django.db.models import get_model
from django.contrib.auth.models import User
import hashlib

class LegacyUserAuthBackend(object):
    def _check_legacy_password(self,password):
        nickname = self.nickname.lower()
        salt = sum([ord(char) for char in nickname]) % len(nickname)
        return user.password == hashlib.sha256(str(salt) + password).hexdigest()
    
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)

            if '$' not in user.password:
                if self._check_legacy_password(password):
                    user.set_password(password)
                    user.save()
                    return user
                else:
                    return None
            else:
                if user.check_password(password):
                    return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
