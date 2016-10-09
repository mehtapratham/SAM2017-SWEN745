from django.db import models
from time import time

# Create your models here.

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


