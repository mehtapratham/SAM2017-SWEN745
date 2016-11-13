from django.contrib import admin

# Register your models here.
from .models import Paper, Author, PCC, PCM, Notification
admin.site.register(Paper)
admin.site.register(Author)
admin.site.register(PCC)
admin.site.register(PCM)
admin.site.register(Notification)