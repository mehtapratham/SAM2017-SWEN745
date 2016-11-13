from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from datetime import datetime, date, time
from django.template.defaulttags import register
from django.db.models import Q
from time import time
from django.utils import timezone


# the templates use this to lookup the text for each enum int
@register.filter
def get_enum(dictionary, key):
    return dictionary[key][1]


class SAMUserManager(BaseUserManager):

    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=self.normalize_email(username),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **kwargs):
        user = self.model(
            username=username,
            is_superuser=True,
            is_admin=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


# User Model
class SAMUser(AbstractBaseUser, PermissionsMixin):
    username = models.EmailField(verbose_name='email address', max_length=255, unique=True, null=False)
    #email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(verbose_name='first name', max_length=30, unique=False, null=False)
    last_name = models.CharField(verbose_name='last name', max_length=30, unique=False, null=True)
    phone_number = models.CharField(verbose_name='phone number', blank=True, max_length=15)
    address = models.CharField(verbose_name='address', max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=None, blank=True)
    #is_staff = models.BooleanField(_('staff status'), default=False,help_text=_('Designates whether the user can log into this admin 'site.'))

    objects = SAMUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Author(SAMUser):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def get_upload_file_name(instance, filename):
    return 'uploaded_files/%s_%s' % (str(time()).replace('.', '_'), filename)


class Paper(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    # upload_date = models.DateField(auto_now_add=True)
    authors = models.ManyToManyField(Author)
    file = models.FileField(upload_to=get_upload_file_name)

    def __str__(self):
        return self.title


class PCC(SAMUser):
    # associated_user = models.ForeignKey(SAMUser, on_delete=models.CASCADE)
    papers_assigned = models.ManyToManyField(Paper)


class PCM(SAMUser):
    # associated_user = models.ForeignKey(SAMUser, on_delete=models.CASCADE)
    paper_selections = models.ManyToManyField(Paper, related_name="paper_selections")
    papers_assigned = models.ManyToManyField(Paper, related_name="papers_assigned")

class Notification(models.Model):
    title = models.CharField(max_length=500, verbose_name=u"Title")
    message = models.TextField(verbose_name=u"Message")
    recipients = models.ManyToManyField(SAMUser)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + '' + self.message

    notification_message_mapper =  {
        'NEW_PAPER': {'title':'New Paper','message':'A new paper has been uploaded.'},
        'SUB_FORMAT_ERROR':{'title':'Submission Format Error','message':'Submission Format Error'},
        'PAPER_ASSIGNED':{'title':'Paper Assigned','message':'A Paper has been assigned to you.'},
        'ASSIGN_PAPER':{'title':'Assignment Pending','message':'There are few papers that are yet to be assigned to committee members. Please review these.'},
        'REVIEW_PAPER':{'title':'Review Pending','message':'A paper assigned to you is pending review.'},
        'FINAL_REVIEW_REQ':{'title':'Provide Final Rating','message':'Reviews from the PCMs are in. Please provide a final review and rating.'},
        'REVIEW_RESULTS':{'title':'Your paper has been reviewed','message':'The review results for a paper you submitted are in.'}
    }

    def sendNotification(self, type, recipients):
        notification = self
        notification.title = self.notification_message_mapper[type]['title']
        notification.message = self.notification_message_mapper[type]['message']
        notification.save()
        notification.recipients.set(recipients)
        print("In here - Saving notifications")
        notification.save()






