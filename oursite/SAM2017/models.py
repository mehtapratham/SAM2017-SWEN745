from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from datetime import datetime, date, time
from django.template.defaulttags import register
from django.db.models import Q

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




#User Model
class SAMUser(AbstractBaseUser, PermissionsMixin):

	username = models.EmailField(verbose_name='email address', max_length=255, unique=True,null=False)
	first_name = models.CharField(verbose_name='first name',max_length=30,unique=False,null=False)
	last_name = models.CharField(verbose_name='last name',max_length=30,unique=False,null=True)
	phone_number = models.CharField(verbose_name='phone number', blank=True, max_length=15)
	is_author= models.BooleanField(default=True)
	is_pcm= models.BooleanField(default=False)
	is_pcc= models.BooleanField(default=False)
	address = models.CharField(verbose_name='address', max_length=255, null=True, blank=True)
	
	objects = SAMUserManager()
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []
	
	def get_full_name(self):
        # The user is identified by their email address
		return self.username
		
	def get_short_name(self):
	# The user is identified by their email address
		return self.username
		
	def __str__(self):
		return self.username
		
	def has_perm(self, perm, obj=None):
		return True
		
	def has_module_perms(self, app_label):
		return True


class Author(models.Model):
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
    #upload_date = models.DateField(auto_now_add=True)
    authors = models.ManyToManyField(Author)
    file = models.FileField(upload_to=get_upload_file_name)

    def __str__(self):
        return self.title


