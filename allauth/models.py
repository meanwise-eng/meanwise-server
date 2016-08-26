from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser

from django.utils.crypto import get_random_string

from mails.mail_types import PasswordChangeMail


def send_change_password_mail(user):
    data = {'token': user.password_reset_token}
    mail = PasswordChangeMail(user.email, data)
    mail.send()


def generate_reset_token(length=32):
    return get_random_string(length)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        '''
        Creates and saves a User with the given email, date of birth
        and password.
        '''
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
                email=self.normalize_email(email),
                )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        '''
        Creates and saves a superuser with the given email, date of
        birth and password.
        '''
        user = self.create_user(
                email,
                password=password,
                )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def reset_password(self, token, password):
        user = self.get(password_reset_token=token)
        user.password_reset_on = timezone.now()
        user.password_reset_token = ''
        user.password_reset_token_sent_on = None
        user.password_reset_count += 1
        user.set_password(password)
        user.save()
        return True

    def change_password(self, user, old_password, new_password):
        if not user.check_password(old_password):
            raise Exception('Invalid Password')
        else:
            user.set_password(new_password)
            user.save()
            return user

    def send_forgot_password_link(self, email):
        user = self.get(email=email)
        user.password_reset_token = generate_reset_token()
        user.password_reset_token_sent_on = timezone.now()
        user.password_reset_count += 1
        user.save()
        send_change_password_mail(user)

class User(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(max_length=128,unique=True,verbose_name='Email', db_index=True)
    created_on      = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active       = models.BooleanField(default=True)
    is_admin        = models.BooleanField(default=False)
    updated_on      = models.DateTimeField(auto_now=True)

    password_reset_token = models.CharField(max_length=64,blank=True, null=True)
    password_reset_token_sent_on = models.DateTimeField(blank=True, null=True)
    password_reset_count = models.IntegerField(default=0)
    password_reset_on    = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):              # __unicode__ on Python 2
        return self.email

    @property
    def is_staff(self):
        '''Is the user a member of staff?'''
        return self.is_admin

    def to_dict(self):
        data = {
                'email': self.email,
                }
        return data

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `Duelify_app`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin